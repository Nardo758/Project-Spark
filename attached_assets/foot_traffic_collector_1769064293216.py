"""
OppGrid Foot Traffic Data Collector
Extracts Google Maps Popular Times data for locations and areas

Usage:
    from utils.foot_traffic_collector import FootTrafficCollector
    
    collector = FootTrafficCollector(api_key, db_connection)
    traffic_data = collector.get_area_traffic(lat, lng, radius=800)
    collector.save_traffic_data(traffic_data)
"""

import populartimes
import googlemaps
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import psycopg2
from psycopg2.extras import Json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
        logger.info("FootTrafficCollector initialized")
        
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
                logger.warning(f"Error fetching place {place_id}: {place['status']}")
                return None
            
            result = place['result']
            
            # Extract location
            location = result['geometry']['location']
            lat = location['lat']
            lng = location['lng']
            
            # Get popular times using populartimes library
            traffic_data = populartimes.get_id(self.api_key, place_id)
            
            if not traffic_data:
                logger.info(f"No traffic data available for {place_id}")
                return None
            
            # Structure the data
            traffic_info = {
                'place_id': place_id,
                'place_name': result.get('name', 'Unknown'),
                'place_address': result.get('formatted_address', ''),
                'place_type': result.get('types', ['unknown'])[0] if result.get('types') else 'unknown',
                'latitude': lat,
                'longitude': lng,
                'popular_times': self._format_popular_times(traffic_data.get('populartimes', [])),
                'current_popularity': traffic_data.get('current_popularity', None),
                'time_spent': traffic_data.get('time_spent', {}),
                'data_quality_score': self._calculate_data_quality(traffic_data)
            }
            
            logger.info(f"Successfully collected traffic for {traffic_info['place_name']}")
            return traffic_info
            
        except Exception as e:
            logger.error(f"Error collecting traffic for place {place_id}: {str(e)}")
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
            
            logger.info(f"Collecting area traffic at ({latitude}, {longitude}) radius {radius_meters}m")
            
            all_traffic_data = []
            seen_place_ids = set()  # Avoid duplicates
            
            for place_type in place_types:
                try:
                    # Search for nearby places of this type
                    places = self.gmaps.places_nearby(
                        location=(latitude, longitude),
                        radius=radius_meters,
                        type=place_type
                    )
                    
                    if places['status'] != 'OK':
                        logger.warning(f"Places API returned status {places['status']} for type {place_type}")
                        continue
                    
                    logger.info(f"Found {len(places.get('results', []))} {place_type}s")
                    
                    # Collect traffic data for each place
                    for place in places.get('results', []):
                        place_id = place.get('place_id')
                        
                        if not place_id or place_id in seen_place_ids:
                            continue
                        
                        seen_place_ids.add(place_id)
                        
                        # Rate limiting - Google allows ~10 requests/second
                        time.sleep(0.15)
                        
                        traffic_data = self.get_place_traffic(place_id)
                        if traffic_data:
                            all_traffic_data.append(traffic_data)
                    
                    # Brief pause between place type searches
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"Error processing place type {place_type}: {str(e)}")
                    continue
            
            logger.info(f"Collected traffic data for {len(all_traffic_data)} locations")
            return all_traffic_data
            
        except Exception as e:
            logger.error(f"Error collecting area traffic: {str(e)}")
            return []
    
    def save_traffic_data(self, traffic_data: List[Dict]) -> int:
        """
        Save traffic data to database with upsert logic
        
        Args:
            traffic_data: List of traffic data dictionaries
            
        Returns:
            Number of records saved
        """
        if not traffic_data:
            logger.warning("No traffic data to save")
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
                    'time_spent_min': time_spent.get('min') if isinstance(time_spent, dict) else None,
                    'time_spent_max': time_spent.get('max') if isinstance(time_spent, dict) else None,
                    'data_quality_score': data.get('data_quality_score', 0.7)
                }
                
                cursor.execute(query, params)
                saved_count += 1
                
            except Exception as e:
                logger.error(f"Error saving traffic data for {data.get('place_id', 'unknown')}: {str(e)}")
                continue
        
        self.db.commit()
        cursor.close()
        
        logger.info(f"Successfully saved {saved_count} traffic records")
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
            if 'day' in day_data and 'data' in day_data:
                day_index = day_data['day']
                if 0 <= day_index < 7:
                    day_name = days[day_index]
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


def test_collector():
    """
    Test function for development
    """
    import os
    
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    db_url = os.getenv('DATABASE_URL')
    
    if not api_key or not db_url:
        print("Missing GOOGLE_MAPS_API_KEY or DATABASE_URL environment variables")
        return
    
    try:
        db_conn = psycopg2.connect(db_url)
        collector = FootTrafficCollector(api_key, db_conn)
        
        # Test with Times Square, NYC
        print("\n=== Testing Foot Traffic Collector ===\n")
        print("Collecting data for area around Times Square, NYC...")
        
        traffic_data = collector.get_area_traffic(
            latitude=40.7589,
            longitude=-73.9851,
            radius_meters=300
        )
        
        print(f"\nCollected data for {len(traffic_data)} locations")
        
        if traffic_data:
            print(f"\nSample location: {traffic_data[0]['place_name']}")
            print(f"Quality score: {traffic_data[0]['data_quality_score']}")
            
            # Save to database
            saved = collector.save_traffic_data(traffic_data)
            print(f"\nSaved {saved} records to database")
        
        db_conn.close()
        print("\n=== Test Complete ===\n")
        
    except Exception as e:
        print(f"Test failed: {str(e)}")


if __name__ == "__main__":
    test_collector()
