# OppGrid Foot Traffic Intelligence Framework
**Google Maps Popular Times Data Collection & Analysis System**

---

## Executive Overview

This framework enables OppGrid to collect, store, and analyze foot traffic data from Google Maps Popular Times without expensive foot traffic APIs. The system triangulates business activity levels for locations and areas, providing critical validation data for opportunity assessment.

**Key Capabilities:**
- Extract hourly foot traffic patterns from Google Maps
- Aggregate area-level traffic from multiple nearby locations
- Identify peak hours and traffic trends
- Validate opportunity demand through real-world activity data
- Cost: $0 (vs $500-2000/month for commercial foot traffic APIs)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      OppGrid Platform                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐  │
│  │ Data Collect │─────▶│   Storage    │─────▶│   Analysis   │  │
│  │   (Python)   │      │ (PostgreSQL) │      │  (Python)    │  │
│  └──────────────┘      └──────────────┘      └──────────────┘  │
│         │                                              │        │
│         │                                              ▼        │
│         │                                    ┌──────────────┐   │
│         │                                    │     API      │   │
│         │                                    │   Endpoint   │   │
│         │                                    └──────────────┘   │
│         │                                              │        │
│         ▼                                              ▼        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         Google Maps Popular Times                        │  │
│  │  (via populartimes or outscraper libraries)              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Database Schema

### 1. Foot Traffic Data Table

```sql
-- Create extension for geographic data
CREATE EXTENSION IF NOT EXISTS postgis;

-- Main foot traffic data table
CREATE TABLE foot_traffic (
    id SERIAL PRIMARY KEY,
    place_id VARCHAR(255) NOT NULL,
    place_name VARCHAR(500) NOT NULL,
    place_address TEXT,
    place_type VARCHAR(100), -- restaurant, retail, service, etc.
    
    -- Geographic data
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    location GEOGRAPHY(POINT, 4326),
    
    -- Traffic data structure (JSON for flexibility)
    popular_times JSONB, -- Hourly data for each day of week
    current_popularity INTEGER, -- Real-time if available (0-100)
    time_spent_min INTEGER, -- Average time people spend (minutes)
    time_spent_max INTEGER,
    
    -- Metadata
    data_source VARCHAR(50) DEFAULT 'google_maps',
    data_quality_score DECIMAL(3, 2), -- 0.0-1.0
    collected_at TIMESTAMP DEFAULT NOW(),
    last_updated TIMESTAMP DEFAULT NOW(),
    
    -- Indexes
    UNIQUE(place_id)
);

-- Create spatial index
CREATE INDEX idx_foot_traffic_location ON foot_traffic USING GIST(location);

-- Create indexes for common queries
CREATE INDEX idx_foot_traffic_place_id ON foot_traffic(place_id);
CREATE INDEX idx_foot_traffic_place_type ON foot_traffic(place_type);
CREATE INDEX idx_foot_traffic_updated ON foot_traffic(last_updated);

-- Example popular_times JSON structure:
/*
{
  "Monday": [0, 0, 0, 0, 0, 0, 12, 25, 45, 67, 78, 85, 80, 75, 60, 45, 50, 65, 70, 55, 40, 20, 10, 5],
  "Tuesday": [...],
  "Wednesday": [...],
  "Thursday": [...],
  "Friday": [...],
  "Saturday": [...],
  "Sunday": [...]
}
*/

-- Add comment explaining the structure
COMMENT ON COLUMN foot_traffic.popular_times IS 
'JSON object with day names as keys and arrays of 24 hourly traffic values (0-100) as values';
```

### 2. Area Traffic Aggregations Table

```sql
-- Pre-computed area-level traffic patterns
CREATE TABLE area_traffic_aggregations (
    id SERIAL PRIMARY KEY,
    area_name VARCHAR(255),
    center_latitude DECIMAL(10, 8) NOT NULL,
    center_longitude DECIMAL(11, 8) NOT NULL,
    center_location GEOGRAPHY(POINT, 4326),
    radius_meters INTEGER NOT NULL DEFAULT 800, -- ~0.5 mile radius
    
    -- Aggregated traffic data
    avg_popular_times JSONB, -- Average traffic pattern for area
    total_locations_sampled INTEGER,
    dominant_place_types JSONB, -- Array of most common business types
    
    -- Peak patterns
    peak_day VARCHAR(20),
    peak_hour INTEGER,
    peak_traffic_score INTEGER,
    
    -- Area vitality metrics
    area_vitality_score DECIMAL(5, 2), -- Composite score 0-100
    business_density_score DECIMAL(5, 2),
    foot_traffic_consistency DECIMAL(5, 2), -- How consistent traffic is
    
    -- Metadata
    computed_at TIMESTAMP DEFAULT NOW(),
    last_refreshed TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_area_traffic_location ON area_traffic_aggregations USING GIST(center_location);
CREATE INDEX idx_area_traffic_vitality ON area_traffic_aggregations(area_vitality_score DESC);
```

### 3. Opportunity Foot Traffic Link

```sql
-- Link opportunities to foot traffic data
CREATE TABLE opportunity_foot_traffic (
    id SERIAL PRIMARY KEY,
    opportunity_id INTEGER REFERENCES opportunities(id) ON DELETE CASCADE,
    
    -- Traffic context for this opportunity
    area_traffic_score DECIMAL(5, 2), -- 0-100
    nearby_traffic_places INTEGER, -- Number of places sampled
    peak_demand_alignment BOOLEAN, -- Does opp align with peak hours?
    
    -- Geographic radius analyzed
    analysis_radius_meters INTEGER DEFAULT 800,
    
    -- Traffic insights (AI generated summary)
    traffic_insights TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(opportunity_id)
);

CREATE INDEX idx_opp_foot_traffic_score ON opportunity_foot_traffic(area_traffic_score DESC);
CREATE INDEX idx_opp_foot_traffic_opp_id ON opportunity_foot_traffic(opportunity_id);
```

---

## Data Collection System

### Installation Requirements

```bash
# In your Replit environment or requirements.txt
pip install populartimes
pip install requests
pip install googlemaps
pip install psycopg2-binary
pip install redis
pip install celery
```

### Core Data Collector (`foot_traffic_collector.py`)

```python
"""
OppGrid Foot Traffic Data Collector
Extracts Google Maps Popular Times data for locations and areas
"""

import populartimes
import googlemaps
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import psycopg2
from psycopg2.extras import Json, execute_values
import os

class FootTrafficCollector:
    """
    Collects foot traffic data from Google Maps Popular Times
    """
    
    def __init__(self, google_api_key: str, db_conn):
        """
        Initialize collector with Google API key and database connection
        
        Args:
            google_api_key: Google Maps API key
            db_conn: PostgreSQL database connection
        """
        self.api_key = google_api_key
        self.gmaps = googlemaps.Client(key=google_api_key)
        self.db = db_conn
        
    def get_place_traffic(self, place_id: str) -> Optional[Dict]:
        """
        Get foot traffic data for a specific Google Place ID
        
        Args:
            place_id: Google Maps Place ID
            
        Returns:
            Dictionary with traffic data or None if unavailable
        """
        try:
            # Get place details first
            place = self.gmaps.place(place_id=place_id)
            
            if place['status'] != 'OK':
                print(f"Error fetching place {place_id}: {place['status']}")
                return None
            
            result = place['result']
            
            # Extract location
            location = result['geometry']['location']
            lat = location['lat']
            lng = location['lng']
            
            # Get popular times using populartimes library
            # This queries Google Maps and extracts the popular times data
            traffic_data = populartimes.get_id(self.api_key, place_id)
            
            if not traffic_data:
                print(f"No traffic data available for {place_id}")
                return None
            
            # Structure the data
            traffic_info = {
                'place_id': place_id,
                'place_name': result.get('name', 'Unknown'),
                'place_address': result.get('formatted_address', ''),
                'place_type': result.get('types', ['unknown'])[0],
                'latitude': lat,
                'longitude': lng,
                'popular_times': self._format_popular_times(traffic_data.get('populartimes', [])),
                'current_popularity': traffic_data.get('current_popularity', None),
                'time_spent': traffic_data.get('time_spent', {}),
                'data_quality_score': self._calculate_data_quality(traffic_data)
            }
            
            return traffic_info
            
        except Exception as e:
            print(f"Error collecting traffic for place {place_id}: {str(e)}")
            return None
    
    def get_area_traffic(self, latitude: float, longitude: float, 
                        radius_meters: int = 800,
                        place_types: List[str] = None) -> List[Dict]:
        """
        Get foot traffic data for all relevant places in an area
        
        Args:
            latitude: Center point latitude
            longitude: Center point longitude
            radius_meters: Search radius (default 800m = ~0.5 miles)
            place_types: Filter by place types (e.g., ['restaurant', 'store'])
            
        Returns:
            List of traffic data dictionaries
        """
        try:
            # Default to key business types if not specified
            if place_types is None:
                place_types = [
                    'restaurant', 'cafe', 'store', 'shopping_mall',
                    'gym', 'bar', 'supermarket', 'convenience_store'
                ]
            
            all_traffic_data = []
            
            for place_type in place_types:
                # Search for nearby places of this type
                places = self.gmaps.places_nearby(
                    location=(latitude, longitude),
                    radius=radius_meters,
                    type=place_type
                )
                
                if places['status'] != 'OK':
                    continue
                
                # Collect traffic data for each place
                for place in places.get('results', []):
                    place_id = place.get('place_id')
                    
                    if place_id:
                        # Rate limiting - Google allows ~10 requests/second
                        time.sleep(0.15)
                        
                        traffic_data = self.get_place_traffic(place_id)
                        if traffic_data:
                            all_traffic_data.append(traffic_data)
                
                # Brief pause between place type searches
                time.sleep(0.5)
            
            return all_traffic_data
            
        except Exception as e:
            print(f"Error collecting area traffic: {str(e)}")
            return []
    
    def save_traffic_data(self, traffic_data: List[Dict]) -> int:
        """
        Save traffic data to database
        
        Args:
            traffic_data: List of traffic data dictionaries
            
        Returns:
            Number of records saved
        """
        if not traffic_data:
            return 0
        
        cursor = self.db.cursor()
        saved_count = 0
        
        for data in traffic_data:
            try:
                # Upsert query (insert or update if exists)
                query = """
                INSERT INTO foot_traffic (
                    place_id, place_name, place_address, place_type,
                    latitude, longitude, location,
                    popular_times, current_popularity,
                    time_spent_min, time_spent_max,
                    data_quality_score, last_updated
                )
                VALUES (
                    %(place_id)s, %(place_name)s, %(place_address)s, %(place_type)s,
                    %(latitude)s, %(longitude)s, ST_MakePoint(%(longitude)s, %(latitude)s)::geography,
                    %(popular_times)s, %(current_popularity)s,
                    %(time_spent_min)s, %(time_spent_max)s,
                    %(data_quality_score)s, NOW()
                )
                ON CONFLICT (place_id) DO UPDATE SET
                    place_name = EXCLUDED.place_name,
                    place_address = EXCLUDED.place_address,
                    popular_times = EXCLUDED.popular_times,
                    current_popularity = EXCLUDED.current_popularity,
                    time_spent_min = EXCLUDED.time_spent_min,
                    time_spent_max = EXCLUDED.time_spent_max,
                    data_quality_score = EXCLUDED.data_quality_score,
                    last_updated = NOW()
                """
                
                # Prepare parameters
                time_spent = data.get('time_spent', {})
                params = {
                    'place_id': data['place_id'],
                    'place_name': data['place_name'],
                    'place_address': data['place_address'],
                    'place_type': data['place_type'],
                    'latitude': data['latitude'],
                    'longitude': data['longitude'],
                    'popular_times': Json(data.get('popular_times')),
                    'current_popularity': data.get('current_popularity'),
                    'time_spent_min': time_spent.get('min'),
                    'time_spent_max': time_spent.get('max'),
                    'data_quality_score': data.get('data_quality_score', 0.7)
                }
                
                cursor.execute(query, params)
                saved_count += 1
                
            except Exception as e:
                print(f"Error saving traffic data for {data['place_id']}: {str(e)}")
                continue
        
        self.db.commit()
        cursor.close()
        
        return saved_count
    
    def _format_popular_times(self, popular_times_data: List) -> Dict:
        """
        Format popular times data into consistent structure
        
        Args:
            popular_times_data: Raw popular times list from API
            
        Returns:
            Formatted dictionary with day names as keys
        """
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        formatted = {}
        
        for day_data in popular_times_data:
            day_name = days[day_data['day']]
            formatted[day_name] = day_data.get('data', [0] * 24)
        
        return formatted
    
    def _calculate_data_quality(self, traffic_data: Dict) -> float:
        """
        Calculate data quality score based on completeness
        
        Args:
            traffic_data: Traffic data dictionary
            
        Returns:
            Quality score 0.0-1.0
        """
        score = 0.0
        
        # Has popular times data
        if traffic_data.get('populartimes'):
            score += 0.5
        
        # Has current popularity
        if traffic_data.get('current_popularity') is not None:
            score += 0.2
        
        # Has time spent data
        if traffic_data.get('time_spent'):
            score += 0.2
        
        # Has complete popular times (all 7 days)
        popular_times = traffic_data.get('populartimes', [])
        if len(popular_times) == 7:
            score += 0.1
        
        return min(score, 1.0)


# Usage example
if __name__ == "__main__":
    # Initialize
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    db_conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    
    collector = FootTrafficCollector(api_key, db_conn)
    
    # Example: Collect data for area around a specific location
    # (e.g., downtown area where an opportunity exists)
    latitude = 40.7589  # Times Square, NYC
    longitude = -73.9851
    
    print(f"Collecting foot traffic data for area around {latitude}, {longitude}")
    traffic_data = collector.get_area_traffic(latitude, longitude, radius_meters=500)
    
    print(f"Collected data for {len(traffic_data)} locations")
    
    # Save to database
    saved = collector.save_traffic_data(traffic_data)
    print(f"Saved {saved} traffic records to database")
    
    db_conn.close()
```

---

## Traffic Analysis System

### Area Traffic Analyzer (`traffic_analyzer.py`)

```python
"""
OppGrid Foot Traffic Analyzer
Aggregates and analyzes foot traffic patterns for areas and opportunities
"""

import psycopg2
from psycopg2.extras import Json
import json
from typing import Dict, List, Tuple
from datetime import datetime
import statistics

class TrafficAnalyzer:
    """
    Analyzes foot traffic patterns and generates insights
    """
    
    def __init__(self, db_conn):
        """
        Initialize analyzer with database connection
        
        Args:
            db_conn: PostgreSQL database connection
        """
        self.db = db_conn
    
    def analyze_area_traffic(self, latitude: float, longitude: float,
                            radius_meters: int = 800) -> Dict:
        """
        Aggregate and analyze foot traffic for an area
        
        Args:
            latitude: Center point latitude
            longitude: Center point longitude
            radius_meters: Analysis radius
            
        Returns:
            Dictionary with aggregated traffic analysis
        """
        cursor = self.db.cursor()
        
        # Query all traffic data within radius
        query = """
        SELECT 
            place_id, place_name, place_type,
            latitude, longitude,
            popular_times, current_popularity,
            time_spent_min, time_spent_max,
            data_quality_score
        FROM foot_traffic
        WHERE ST_DWithin(
            location,
            ST_MakePoint(%s, %s)::geography,
            %s
        )
        AND popular_times IS NOT NULL
        ORDER BY data_quality_score DESC
        """
        
        cursor.execute(query, (longitude, latitude, radius_meters))
        results = cursor.fetchall()
        
        if not results:
            return self._empty_analysis()
        
        # Aggregate traffic patterns
        all_traffic_patterns = []
        place_types_count = {}
        total_current_popularity = []
        
        for row in results:
            place_id, place_name, place_type, lat, lng, popular_times, \
            current_pop, time_min, time_max, quality = row
            
            # Collect traffic patterns
            if popular_times:
                all_traffic_patterns.append(popular_times)
            
            # Count place types
            place_types_count[place_type] = place_types_count.get(place_type, 0) + 1
            
            # Track current popularity
            if current_pop is not None:
                total_current_popularity.append(current_pop)
        
        # Calculate aggregate metrics
        avg_popular_times = self._average_traffic_patterns(all_traffic_patterns)
        peak_day, peak_hour, peak_value = self._find_peak_traffic(avg_popular_times)
        
        # Calculate area vitality score
        vitality_score = self._calculate_vitality_score(
            len(results),
            avg_popular_times,
            place_types_count,
            total_current_popularity
        )
        
        # Determine dominant place types
        dominant_types = sorted(
            place_types_count.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        analysis = {
            'center_latitude': latitude,
            'center_longitude': longitude,
            'radius_meters': radius_meters,
            'total_locations_sampled': len(results),
            'avg_popular_times': avg_popular_times,
            'peak_day': peak_day,
            'peak_hour': peak_hour,
            'peak_traffic_score': peak_value,
            'current_avg_popularity': statistics.mean(total_current_popularity) if total_current_popularity else None,
            'area_vitality_score': vitality_score,
            'business_density_score': self._calculate_business_density(len(results), radius_meters),
            'traffic_consistency': self._calculate_consistency(all_traffic_patterns),
            'dominant_place_types': dict(dominant_types),
            'generated_at': datetime.now().isoformat()
        }
        
        cursor.close()
        return analysis
    
    def link_opportunity_traffic(self, opportunity_id: int,
                                 opportunity_lat: float, opportunity_lng: float,
                                 radius_meters: int = 800) -> Dict:
        """
        Link an opportunity to surrounding foot traffic data
        
        Args:
            opportunity_id: OppGrid opportunity ID
            opportunity_lat: Opportunity latitude
            opportunity_lng: Opportunity longitude
            radius_meters: Analysis radius
            
        Returns:
            Traffic insights for this opportunity
        """
        # Get area traffic analysis
        area_analysis = self.analyze_area_traffic(
            opportunity_lat, opportunity_lng, radius_meters
        )
        
        if not area_analysis or area_analysis['total_locations_sampled'] == 0:
            return None
        
        # Generate AI insights (would call DeepSeek/Claude here)
        insights = self._generate_traffic_insights(area_analysis)
        
        # Save to database
        cursor = self.db.cursor()
        
        query = """
        INSERT INTO opportunity_foot_traffic (
            opportunity_id, area_traffic_score, nearby_traffic_places,
            peak_demand_alignment, analysis_radius_meters,
            traffic_insights, updated_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, NOW())
        ON CONFLICT (opportunity_id) DO UPDATE SET
            area_traffic_score = EXCLUDED.area_traffic_score,
            nearby_traffic_places = EXCLUDED.nearby_traffic_places,
            peak_demand_alignment = EXCLUDED.peak_demand_alignment,
            traffic_insights = EXCLUDED.traffic_insights,
            updated_at = NOW()
        """
        
        cursor.execute(query, (
            opportunity_id,
            area_analysis['area_vitality_score'],
            area_analysis['total_locations_sampled'],
            area_analysis['peak_traffic_score'] > 70,  # High peak traffic
            radius_meters,
            insights
        ))
        
        self.db.commit()
        cursor.close()
        
        return {
            'opportunity_id': opportunity_id,
            'traffic_score': area_analysis['area_vitality_score'],
            'insights': insights,
            'detailed_analysis': area_analysis
        }
    
    def _average_traffic_patterns(self, patterns: List[Dict]) -> Dict:
        """
        Average multiple traffic patterns into one aggregate pattern
        
        Args:
            patterns: List of popular_times dictionaries
            
        Returns:
            Averaged popular_times dictionary
        """
        if not patterns:
            return {}
        
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        averaged = {}
        
        for day in days:
            hourly_values = []
            
            for pattern in patterns:
                if day in pattern and pattern[day]:
                    hourly_values.append(pattern[day])
            
            if hourly_values:
                # Average each hour across all locations
                averaged[day] = [
                    round(statistics.mean([hours[i] for hours in hourly_values]))
                    for i in range(24)
                ]
            else:
                averaged[day] = [0] * 24
        
        return averaged
    
    def _find_peak_traffic(self, popular_times: Dict) -> Tuple[str, int, int]:
        """
        Find the peak traffic day and hour
        
        Args:
            popular_times: Averaged popular times dictionary
            
        Returns:
            Tuple of (peak_day, peak_hour, peak_value)
        """
        peak_day = None
        peak_hour = None
        peak_value = 0
        
        for day, hours in popular_times.items():
            for hour, value in enumerate(hours):
                if value > peak_value:
                    peak_value = value
                    peak_day = day
                    peak_hour = hour
        
        return peak_day, peak_hour, peak_value
    
    def _calculate_vitality_score(self, num_locations: int,
                                 avg_traffic: Dict,
                                 place_types: Dict,
                                 current_popularity: List) -> float:
        """
        Calculate area vitality score (0-100)
        
        Factors:
        - Business density
        - Average foot traffic levels
        - Traffic consistency across week
        - Diversity of business types
        
        Args:
            num_locations: Number of locations sampled
            avg_traffic: Average traffic patterns
            place_types: Dictionary of place type counts
            current_popularity: List of current popularity values
            
        Returns:
            Vitality score 0-100
        """
        score = 0.0
        
        # Business density component (0-30 points)
        # More locations = higher score
        density_score = min(num_locations / 50.0 * 30, 30)
        score += density_score
        
        # Average traffic level component (0-35 points)
        if avg_traffic:
            all_values = []
            for day in avg_traffic.values():
                all_values.extend(day)
            avg_traffic_level = statistics.mean(all_values) if all_values else 0
            traffic_score = (avg_traffic_level / 100.0) * 35
            score += traffic_score
        
        # Business diversity component (0-20 points)
        diversity_score = min(len(place_types) / 10.0 * 20, 20)
        score += diversity_score
        
        # Current activity component (0-15 points)
        if current_popularity:
            current_score = (statistics.mean(current_popularity) / 100.0) * 15
            score += current_score
        
        return round(score, 2)
    
    def _calculate_business_density(self, num_locations: int,
                                   radius_meters: int) -> float:
        """
        Calculate business density score
        
        Args:
            num_locations: Number of locations
            radius_meters: Search radius
            
        Returns:
            Density score 0-100
        """
        # Calculate locations per square kilometer
        area_sq_km = (3.14159 * (radius_meters ** 2)) / 1_000_000
        density = num_locations / area_sq_km
        
        # Normalize to 0-100 scale (50 businesses/sq km = 100 score)
        score = min((density / 50.0) * 100, 100)
        
        return round(score, 2)
    
    def _calculate_consistency(self, patterns: List[Dict]) -> float:
        """
        Calculate traffic consistency across patterns
        
        Args:
            patterns: List of traffic patterns
            
        Returns:
            Consistency score 0-100 (100 = very consistent)
        """
        if not patterns or len(patterns) < 2:
            return 50.0  # Default for insufficient data
        
        # Calculate standard deviation across all hour/day combinations
        all_stdevs = []
        
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for day in days:
            for hour in range(24):
                values = []
                for pattern in patterns:
                    if day in pattern and pattern[day]:
                        values.append(pattern[day][hour])
                
                if len(values) > 1:
                    stdev = statistics.stdev(values)
                    all_stdevs.append(stdev)
        
        if not all_stdevs:
            return 50.0
        
        # Lower standard deviation = higher consistency
        avg_stdev = statistics.mean(all_stdevs)
        
        # Convert to 0-100 score (inverse relationship)
        # Stdev of 0 = 100, stdev of 50+ = 0
        consistency = max(0, 100 - (avg_stdev * 2))
        
        return round(consistency, 2)
    
    def _generate_traffic_insights(self, analysis: Dict) -> str:
        """
        Generate human-readable insights from traffic analysis
        
        Args:
            analysis: Area traffic analysis dictionary
            
        Returns:
            Formatted insights string
        """
        insights = []
        
        # Vitality assessment
        vitality = analysis['area_vitality_score']
        if vitality >= 75:
            insights.append(f"High-traffic area (vitality score: {vitality}/100)")
        elif vitality >= 50:
            insights.append(f"Moderate-traffic area (vitality score: {vitality}/100)")
        else:
            insights.append(f"Lower-traffic area (vitality score: {vitality}/100)")
        
        # Peak times
        insights.append(
            f"Peak traffic: {analysis['peak_day']}s at {analysis['peak_hour']}:00 "
            f"(traffic level: {analysis['peak_traffic_score']}/100)"
        )
        
        # Business composition
        dominant = list(analysis['dominant_place_types'].items())[:3]
        if dominant:
            types_str = ", ".join([f"{count} {ptype}s" for ptype, count in dominant])
            insights.append(f"Area composition: {types_str}")
        
        # Consistency
        consistency = analysis['traffic_consistency']
        if consistency >= 70:
            insights.append("Consistent traffic patterns throughout the week")
        elif consistency < 50:
            insights.append("Variable traffic patterns - may indicate weekend/weekday differences")
        
        return " | ".join(insights)
    
    def _empty_analysis(self) -> Dict:
        """
        Return empty analysis structure
        """
        return {
            'total_locations_sampled': 0,
            'area_vitality_score': 0,
            'error': 'No traffic data available for this area'
        }


# Usage example
if __name__ == "__main__":
    import os
    
    db_conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    analyzer = TrafficAnalyzer(db_conn)
    
    # Example: Analyze area traffic
    analysis = analyzer.analyze_area_traffic(
        latitude=40.7589,
        longitude=-73.9851,
        radius_meters=500
    )
    
    print(json.dumps(analysis, indent=2))
    
    db_conn.close()
```

---

## API Integration

### Flask API Endpoints (`api/foot_traffic.py`)

```python
"""
OppGrid Foot Traffic API Endpoints
"""

from flask import Blueprint, request, jsonify
from ..utils.foot_traffic_collector import FootTrafficCollector
from ..utils.traffic_analyzer import TrafficAnalyzer
from ..utils.auth import require_auth, get_current_user
from ..database import get_db_connection
import os

foot_traffic_bp = Blueprint('foot_traffic', __name__, url_prefix='/api/foot_traffic')


@foot_traffic_bp.route('/collect/area', methods=['POST'])
@require_auth(['admin'])  # Admin only for data collection
def collect_area_traffic():
    """
    Collect foot traffic data for an area
    
    POST /api/foot_traffic/collect/area
    Body:
    {
        "latitude": 40.7589,
        "longitude": -73.9851,
        "radius_meters": 800,
        "place_types": ["restaurant", "store"]  # Optional
    }
    """
    data = request.get_json()
    
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    radius_meters = data.get('radius_meters', 800)
    place_types = data.get('place_types')
    
    if not latitude or not longitude:
        return jsonify({'error': 'Missing latitude or longitude'}), 400
    
    try:
        db_conn = get_db_connection()
        collector = FootTrafficCollector(
            os.getenv('GOOGLE_MAPS_API_KEY'),
            db_conn
        )
        
        # Collect data
        traffic_data = collector.get_area_traffic(
            latitude, longitude,
            radius_meters=radius_meters,
            place_types=place_types
        )
        
        # Save to database
        saved_count = collector.save_traffic_data(traffic_data)
        
        db_conn.close()
        
        return jsonify({
            'success': True,
            'locations_collected': len(traffic_data),
            'locations_saved': saved_count,
            'area': {
                'latitude': latitude,
                'longitude': longitude,
                'radius_meters': radius_meters
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@foot_traffic_bp.route('/analyze/area', methods=['POST'])
@require_auth(['pro', 'enterprise'])  # Pro/Enterprise users only
def analyze_area_traffic():
    """
    Analyze aggregated foot traffic for an area
    
    POST /api/foot_traffic/analyze/area
    Body:
    {
        "latitude": 40.7589,
        "longitude": -73.9851,
        "radius_meters": 800
    }
    """
    data = request.get_json()
    
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    radius_meters = data.get('radius_meters', 800)
    
    if not latitude or not longitude:
        return jsonify({'error': 'Missing latitude or longitude'}), 400
    
    try:
        db_conn = get_db_connection()
        analyzer = TrafficAnalyzer(db_conn)
        
        analysis = analyzer.analyze_area_traffic(
            latitude, longitude,
            radius_meters=radius_meters
        )
        
        db_conn.close()
        
        return jsonify({
            'success': True,
            'analysis': analysis
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@foot_traffic_bp.route('/opportunity/<int:opportunity_id>', methods=['GET'])
@require_auth(['pro', 'enterprise'])
def get_opportunity_traffic(opportunity_id):
    """
    Get foot traffic analysis for a specific opportunity
    
    GET /api/foot_traffic/opportunity/<opportunity_id>
    """
    user = get_current_user()
    
    try:
        db_conn = get_db_connection()
        cursor = db_conn.cursor()
        
        # Get opportunity location
        cursor.execute("""
            SELECT latitude, longitude
            FROM opportunities
            WHERE id = %s
        """, (opportunity_id,))
        
        opp = cursor.fetchone()
        
        if not opp:
            return jsonify({'error': 'Opportunity not found'}), 404
        
        opp_lat, opp_lng = opp
        
        # Check if we have cached traffic analysis
        cursor.execute("""
            SELECT 
                area_traffic_score, nearby_traffic_places,
                peak_demand_alignment, traffic_insights,
                updated_at
            FROM opportunity_foot_traffic
            WHERE opportunity_id = %s
        """, (opportunity_id,))
        
        cached = cursor.fetchone()
        
        if cached:
            # Return cached analysis
            score, places, peak_align, insights, updated = cached
            
            response = {
                'success': True,
                'opportunity_id': opportunity_id,
                'traffic_data': {
                    'area_traffic_score': float(score),
                    'nearby_traffic_places': places,
                    'peak_demand_alignment': peak_align,
                    'insights': insights,
                    'last_updated': updated.isoformat()
                },
                'cached': True
            }
        else:
            # Generate new analysis
            analyzer = TrafficAnalyzer(db_conn)
            
            traffic_analysis = analyzer.link_opportunity_traffic(
                opportunity_id,
                opp_lat, opp_lng,
                radius_meters=800
            )
            
            if not traffic_analysis:
                response = {
                    'success': True,
                    'opportunity_id': opportunity_id,
                    'traffic_data': None,
                    'message': 'No traffic data available for this location'
                }
            else:
                response = {
                    'success': True,
                    'opportunity_id': opportunity_id,
                    'traffic_data': traffic_analysis,
                    'cached': False
                }
        
        cursor.close()
        db_conn.close()
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@foot_traffic_bp.route('/heatmap', methods=['POST'])
@require_auth(['pro', 'enterprise'])
def get_traffic_heatmap():
    """
    Get traffic data for heatmap visualization
    
    POST /api/foot_traffic/heatmap
    Body:
    {
        "bounds": {
            "north": 40.8,
            "south": 40.7,
            "east": -73.9,
            "west": -74.0
        },
        "day": "Monday",  # Optional
        "hour": 12  # Optional
    }
    """
    data = request.get_json()
    bounds = data.get('bounds')
    day = data.get('day')
    hour = data.get('hour')
    
    if not bounds:
        return jsonify({'error': 'Missing bounds'}), 400
    
    try:
        db_conn = get_db_connection()
        cursor = db_conn.cursor()
        
        # Query traffic data within bounds
        query = """
        SELECT 
            latitude, longitude,
            popular_times, current_popularity
        FROM foot_traffic
        WHERE latitude BETWEEN %s AND %s
          AND longitude BETWEEN %s AND %s
          AND popular_times IS NOT NULL
        """
        
        cursor.execute(query, (
            bounds['south'], bounds['north'],
            bounds['west'], bounds['east']
        ))
        
        results = cursor.fetchall()
        
        # Format for heatmap
        heatmap_data = []
        
        for lat, lng, popular_times, current_pop in results:
            # Calculate intensity based on requested time or average
            if day and hour is not None and popular_times:
                intensity = popular_times.get(day, [0] * 24)[hour]
            elif current_pop is not None:
                intensity = current_pop
            else:
                # Average all traffic
                all_values = []
                for day_data in popular_times.values():
                    all_values.extend(day_data)
                intensity = sum(all_values) / len(all_values) if all_values else 0
            
            heatmap_data.append({
                'lat': float(lat),
                'lng': float(lng),
                'intensity': intensity
            })
        
        cursor.close()
        db_conn.close()
        
        return jsonify({
            'success': True,
            'data': heatmap_data,
            'total_points': len(heatmap_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

---

## Celery Background Tasks

### Scheduled Data Collection (`tasks/foot_traffic_tasks.py`)

```python
"""
Celery tasks for automated foot traffic data collection
"""

from celery import Celery
from ..utils.foot_traffic_collector import FootTrafficCollector
from ..utils.traffic_analyzer import TrafficAnalyzer
from ..database import get_db_connection
import os

celery_app = Celery('oppgrid')
celery_app.config_from_object('oppgrid.celeryconfig')


@celery_app.task(name='collect_opportunity_traffic')
def collect_opportunity_traffic(opportunity_id: int):
    """
    Collect foot traffic data for a specific opportunity
    
    Args:
        opportunity_id: OppGrid opportunity ID
    """
    db_conn = get_db_connection()
    cursor = db_conn.cursor()
    
    try:
        # Get opportunity location
        cursor.execute("""
            SELECT latitude, longitude, title
            FROM opportunities
            WHERE id = %s
        """, (opportunity_id,))
        
        result = cursor.fetchone()
        
        if not result:
            print(f"Opportunity {opportunity_id} not found")
            return
        
        lat, lng, title = result
        
        print(f"Collecting traffic for opportunity {opportunity_id}: {title}")
        
        # Collect traffic data
        collector = FootTrafficCollector(
            os.getenv('GOOGLE_MAPS_API_KEY'),
            db_conn
        )
        
        traffic_data = collector.get_area_traffic(
            lat, lng,
            radius_meters=800
        )
        
        if traffic_data:
            saved = collector.save_traffic_data(traffic_data)
            print(f"Saved {saved} traffic records")
            
            # Analyze and link to opportunity
            analyzer = TrafficAnalyzer(db_conn)
            analysis = analyzer.link_opportunity_traffic(opportunity_id, lat, lng)
            
            print(f"Completed traffic analysis for opportunity {opportunity_id}")
            print(f"Traffic score: {analysis.get('traffic_score', 'N/A')}")
        else:
            print(f"No traffic data collected for opportunity {opportunity_id}")
        
    except Exception as e:
        print(f"Error collecting traffic for opportunity {opportunity_id}: {str(e)}")
    finally:
        cursor.close()
        db_conn.close()


@celery_app.task(name='refresh_area_traffic')
def refresh_area_traffic(latitude: float, longitude: float, radius_meters: int = 800):
    """
    Refresh foot traffic data for an area
    
    Args:
        latitude: Center latitude
        longitude: Center longitude
        radius_meters: Search radius
    """
    db_conn = get_db_connection()
    
    try:
        print(f"Refreshing traffic for area: {latitude}, {longitude}")
        
        collector = FootTrafficCollector(
            os.getenv('GOOGLE_MAPS_API_KEY'),
            db_conn
        )
        
        traffic_data = collector.get_area_traffic(
            latitude, longitude,
            radius_meters=radius_meters
        )
        
        if traffic_data:
            saved = collector.save_traffic_data(traffic_data)
            print(f"Refreshed {saved} traffic records")
        else:
            print(f"No traffic data available for area")
        
    except Exception as e:
        print(f"Error refreshing area traffic: {str(e)}")
    finally:
        db_conn.close()


@celery_app.task(name='bulk_traffic_collection')
def bulk_traffic_collection():
    """
    Collect traffic data for all active opportunities (scheduled task)
    Run this weekly to keep traffic data fresh
    """
    db_conn = get_db_connection()
    cursor = db_conn.cursor()
    
    try:
        # Get all opportunities that need traffic updates
        cursor.execute("""
            SELECT id, latitude, longitude
            FROM opportunities
            WHERE latitude IS NOT NULL
              AND longitude IS NOT NULL
              AND status = 'active'
        """)
        
        opportunities = cursor.fetchall()
        
        print(f"Starting bulk traffic collection for {len(opportunities)} opportunities")
        
        for opp_id, lat, lng in opportunities:
            # Queue individual collection tasks
            collect_opportunity_traffic.delay(opp_id)
        
        print("Bulk traffic collection tasks queued")
        
    except Exception as e:
        print(f"Error in bulk traffic collection: {str(e)}")
    finally:
        cursor.close()
        db_conn.close()
```

---

## Frontend Integration

### JavaScript Client for Traffic Visualization

```javascript
// js/foot-traffic-client.js

/**
 * OppGrid Foot Traffic Client
 * Frontend utilities for displaying foot traffic data
 */

class FootTrafficClient {
    constructor(apiBaseUrl) {
        this.apiBaseUrl = apiBaseUrl;
    }
    
    /**
     * Get foot traffic analysis for an opportunity
     */
    async getOpportunityTraffic(opportunityId) {
        try {
            const response = await fetch(
                `${this.apiBaseUrl}/foot_traffic/opportunity/${opportunityId}`,
                {
                    headers: {
                        'Authorization': `Bearer ${this.getAuthToken()}`
                    }
                }
            );
            
            if (!response.ok) {
                throw new Error('Failed to fetch traffic data');
            }
            
            const data = await response.json();
            return data;
            
        } catch (error) {
            console.error('Error fetching opportunity traffic:', error);
            return null;
        }
    }
    
    /**
     * Display traffic score badge
     */
    renderTrafficBadge(trafficScore, container) {
        const badge = document.createElement('div');
        badge.className = 'traffic-badge';
        
        // Color code based on score
        let color, label;
        if (trafficScore >= 75) {
            color = '#22c55e';  // Green
            label = 'High Traffic';
        } else if (trafficScore >= 50) {
            color = '#f59e0b';  // Orange
            label = 'Moderate Traffic';
        } else {
            color = '#ef4444';  // Red
            label = 'Lower Traffic';
        }
        
        badge.innerHTML = `
            <div style="display: inline-flex; align-items: center; padding: 6px 12px; 
                        background: ${color}20; border: 1px solid ${color}; 
                        border-radius: 6px; font-size: 13px; color: ${color};">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" 
                     stroke="${color}" stroke-width="2" style="margin-right: 6px;">
                    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                    <circle cx="9" cy="7" r="4"></circle>
                    <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                    <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
                </svg>
                <span>${label}: ${trafficScore}/100</span>
            </div>
        `;
        
        container.appendChild(badge);
    }
    
    /**
     * Render traffic insights
     */
    renderTrafficInsights(trafficData, container) {
        if (!trafficData || !trafficData.insights) {
            container.innerHTML = '<p style="color: #6b7280;">No traffic data available</p>';
            return;
        }
        
        const section = document.createElement('div');
        section.className = 'traffic-insights-section';
        section.innerHTML = `
            <h3 style="font-size: 16px; font-weight: 600; margin-bottom: 12px; color: #1a1a1a;">
                📊 Foot Traffic Analysis
            </h3>
            <div style="background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px;">
                <p style="color: #374151; line-height: 1.6; margin: 0;">
                    ${trafficData.insights}
                </p>
                <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid #e5e7eb;">
                    <span style="font-size: 13px; color: #6b7280;">
                        Based on ${trafficData.nearby_traffic_places} nearby locations
                    </span>
                </div>
            </div>
        `;
        
        container.appendChild(section);
    }
    
    /**
     * Get heatmap data for map visualization
     */
    async getHeatmapData(bounds, day = null, hour = null) {
        try {
            const response = await fetch(
                `${this.apiBaseUrl}/foot_traffic/heatmap`,
                {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${this.getAuthToken()}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ bounds, day, hour })
                }
            );
            
            if (!response.ok) {
                throw new Error('Failed to fetch heatmap data');
            }
            
            const data = await response.json();
            return data.data;
            
        } catch (error) {
            console.error('Error fetching heatmap data:', error);
            return [];
        }
    }
    
    /**
     * Render traffic heatmap on Mapbox map
     */
    async renderHeatmap(map, bounds) {
        const heatmapData = await this.getHeatmapData(bounds);
        
        if (!heatmapData || heatmapData.length === 0) {
            console.log('No heatmap data available');
            return;
        }
        
        // Convert to GeoJSON
        const geojson = {
            type: 'FeatureCollection',
            features: heatmapData.map(point => ({
                type: 'Feature',
                geometry: {
                    type: 'Point',
                    coordinates: [point.lng, point.lat]
                },
                properties: {
                    intensity: point.intensity
                }
            }))
        };
        
        // Add source
        if (map.getSource('foot-traffic')) {
            map.getSource('foot-traffic').setData(geojson);
        } else {
            map.addSource('foot-traffic', {
                type: 'geojson',
                data: geojson
            });
            
            // Add heatmap layer
            map.addLayer({
                id: 'foot-traffic-heat',
                type: 'heatmap',
                source: 'foot-traffic',
                paint: {
                    'heatmap-weight': [
                        'interpolate',
                        ['linear'],
                        ['get', 'intensity'],
                        0, 0,
                        100, 1
                    ],
                    'heatmap-intensity': [
                        'interpolate',
                        ['linear'],
                        ['zoom'],
                        0, 1,
                        15, 3
                    ],
                    'heatmap-color': [
                        'interpolate',
                        ['linear'],
                        ['heatmap-density'],
                        0, 'rgba(33, 102, 172, 0)',
                        0.2, 'rgb(103, 169, 207)',
                        0.4, 'rgb(209, 229, 240)',
                        0.6, 'rgb(253, 219, 199)',
                        0.8, 'rgb(239, 138, 98)',
                        1, 'rgb(178, 24, 43)'
                    ],
                    'heatmap-radius': [
                        'interpolate',
                        ['linear'],
                        ['zoom'],
                        0, 2,
                        15, 20
                    ]
                }
            });
        }
    }
    
    getAuthToken() {
        return localStorage.getItem('oppgrid_auth_token');
    }
}

// Export for use in other scripts
window.FootTrafficClient = FootTrafficClient;
```

---

## Implementation Checklist

### Phase 1: Setup (Week 1)
- [ ] Run database migration to create foot_traffic tables
- [ ] Install required Python libraries (populartimes, googlemaps)
- [ ] Get Google Maps API key and configure environment variables
- [ ] Test basic data collection with single location
- [ ] Verify data is saving to PostgreSQL correctly

### Phase 2: Data Collection (Week 1-2)
- [ ] Deploy FootTrafficCollector class
- [ ] Create Celery tasks for automated collection
- [ ] Set up scheduled jobs (weekly refresh)
- [ ] Collect initial dataset for top 50 opportunities
- [ ] Monitor API usage and costs

### Phase 3: Analysis System (Week 2)
- [ ] Deploy TrafficAnalyzer class
- [ ] Test area aggregation logic
- [ ] Link opportunities to traffic data
- [ ] Validate vitality score calculations
- [ ] Generate sample insights

### Phase 4: API Integration (Week 3)
- [ ] Create Flask API endpoints
- [ ] Add authentication/authorization
- [ ] Test all endpoints with Postman
- [ ] Document API in Swagger/OpenAPI
- [ ] Set up rate limiting

### Phase 5: Frontend Integration (Week 3-4)
- [ ] Create JavaScript client library
- [ ] Add traffic badges to opportunity cards
- [ ] Display insights in opportunity details
- [ ] Implement heatmap visualization
- [ ] Add to validation tier features

### Phase 6: Optimization (Week 4)
- [ ] Add Redis caching for frequently accessed areas
- [ ] Optimize database queries with indexes
- [ ] Implement batch collection for efficiency
- [ ] Set up monitoring and alerts
- [ ] Load testing

---

## Cost & Usage Analysis

### Google Maps API Costs

**Popular Times Data:**
- Uses Places API and possibly a scraping approach
- Google doesn't officially provide Popular Times via API
- The `populartimes` library uses Places API which costs:
  - $17 per 1,000 Place Details requests
  - $17 per 1,000 Nearby Search requests

**Estimated Monthly Costs:**

| Usage Level | Locations/Month | API Calls | Estimated Cost |
|-------------|----------------|-----------|----------------|
| MVP (100 opps) | 5,000 | ~10,000 | $170/month |
| Growth (500 opps) | 25,000 | ~50,000 | $850/month |
| Scale (2000 opps) | 100,000 | ~200,000 | $3,400/month |

**Cost Optimization Strategies:**
1. Cache data for 7 days (traffic patterns don't change daily)
2. Collect only for premium tier opportunities initially
3. Batch collection during off-peak hours
4. Focus on high-quality, high-confidence opportunities first

---

## Usage Patterns

### When to Collect Traffic Data

1. **New Opportunity Validation** - Collect immediately when opportunity is discovered
2. **Weekly Refresh** - Update existing data every 7 days
3. **User Request** - Pro/Enterprise users can request fresh data
4. **Geographic Expansion** - When entering new markets

### Who Gets Access

- **Free Tier**: No access (show upgrade prompt)
- **Pro Tier**: View traffic score and basic insights
- **Enterprise Tier**: Full access including heatmaps and detailed analytics

---

## Integration with Existing OppGrid Features

### Validation Studio Enhancement

Add foot traffic as validation signal:
- **Demand Signal**: High traffic = high potential customer base
- **Location Validation**: Confirms location has existing activity
- **Competition Indicator**: Multiple similar businesses = proven market

### Geographic Intelligence

Enhance existing geographic features:
- Layer traffic heatmaps on opportunity maps
- Filter opportunities by traffic levels
- Identify "hot zones" with high opportunity + high traffic

### Consultant Studio Reports

Include in validation reports:
- "Foot Traffic Analysis" section
- Peak hours/days insights
- Customer availability patterns
- Competitive density metrics

---

## Next Steps

1. **Start with Schema** - Run the SQL migration first
2. **Test Collection** - Manually test with 3-5 locations
3. **Deploy Collector** - Add to Replit environment
4. **Link to Opportunities** - Connect first 10 opportunities
5. **Add to Frontend** - Display in opportunity cards

Would you like me to:
1. Create the complete Replit deployment package?
2. Build the frontend UI components?
3. Set up the Celery task scheduler?
4. Create example visualizations?
