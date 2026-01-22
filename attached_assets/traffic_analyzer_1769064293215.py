"""
OppGrid Foot Traffic Analyzer
Aggregates and analyzes foot traffic patterns for areas and opportunities

Usage:
    from utils.traffic_analyzer import TrafficAnalyzer
    
    analyzer = TrafficAnalyzer(db_connection)
    analysis = analyzer.analyze_area_traffic(lat, lng, radius=800)
    analyzer.link_opportunity_traffic(opp_id, lat, lng)
"""

import psycopg2
from psycopg2.extras import Json
import json
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import statistics
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
        logger.info("TrafficAnalyzer initialized")
    
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
        
        try:
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
                logger.info(f"No traffic data found for area ({latitude}, {longitude})")
                return self._empty_analysis()
            
            logger.info(f"Found {len(results)} locations with traffic data")
            
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
            
            logger.info(f"Analysis complete: Vitality score {vitality_score}/100")
            cursor.close()
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing area traffic: {str(e)}")
            cursor.close()
            return self._empty_analysis()
    
    def link_opportunity_traffic(self, opportunity_id: int,
                                 opportunity_lat: float, opportunity_lng: float,
                                 radius_meters: int = 800) -> Optional[Dict]:
        """
        Link an opportunity to surrounding foot traffic data
        
        Args:
            opportunity_id: OppGrid opportunity ID
            opportunity_lat: Opportunity latitude
            opportunity_lng: Opportunity longitude
            radius_meters: Analysis radius
            
        Returns:
            Traffic insights for this opportunity or None
        """
        logger.info(f"Linking traffic data to opportunity {opportunity_id}")
        
        # Get area traffic analysis
        area_analysis = self.analyze_area_traffic(
            opportunity_lat, opportunity_lng, radius_meters
        )
        
        if not area_analysis or area_analysis['total_locations_sampled'] == 0:
            logger.warning(f"No traffic data available for opportunity {opportunity_id}")
            return None
        
        # Generate insights
        insights = self._generate_traffic_insights(area_analysis)
        
        # Save to database
        cursor = self.db.cursor()
        
        try:
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
            
            logger.info(f"Successfully linked traffic data to opportunity {opportunity_id}")
            
            return {
                'opportunity_id': opportunity_id,
                'traffic_score': area_analysis['area_vitality_score'],
                'insights': insights,
                'detailed_analysis': area_analysis
            }
            
        except Exception as e:
            logger.error(f"Error linking traffic to opportunity {opportunity_id}: {str(e)}")
            cursor.close()
            return None
    
    def get_opportunity_traffic(self, opportunity_id: int) -> Optional[Dict]:
        """
        Get cached traffic analysis for an opportunity
        
        Args:
            opportunity_id: OppGrid opportunity ID
            
        Returns:
            Cached traffic analysis or None
        """
        cursor = self.db.cursor()
        
        try:
            query = """
            SELECT 
                area_traffic_score, nearby_traffic_places,
                peak_demand_alignment, traffic_insights,
                analysis_radius_meters, updated_at
            FROM opportunity_foot_traffic
            WHERE opportunity_id = %s
            """
            
            cursor.execute(query, (opportunity_id,))
            result = cursor.fetchone()
            
            if not result:
                return None
            
            score, places, peak_align, insights, radius, updated = result
            
            cursor.close()
            
            return {
                'opportunity_id': opportunity_id,
                'area_traffic_score': float(score),
                'nearby_traffic_places': places,
                'peak_demand_alignment': peak_align,
                'insights': insights,
                'analysis_radius_meters': radius,
                'last_updated': updated.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error fetching opportunity traffic: {str(e)}")
            cursor.close()
            return None
    
    def _average_traffic_patterns(self, patterns: List[Dict]) -> Dict:
        """
        Average multiple traffic patterns into one aggregate pattern
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
        - Business density (0-30 points)
        - Average foot traffic levels (0-35 points)
        - Business diversity (0-20 points)
        - Current activity (0-15 points)
        """
        score = 0.0
        
        # Business density component (0-30 points)
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
        Calculate business density score (0-100)
        """
        # Calculate locations per square kilometer
        area_sq_km = (3.14159 * (radius_meters ** 2)) / 1_000_000
        density = num_locations / area_sq_km if area_sq_km > 0 else 0
        
        # Normalize to 0-100 scale (50 businesses/sq km = 100 score)
        score = min((density / 50.0) * 100, 100)
        
        return round(score, 2)
    
    def _calculate_consistency(self, patterns: List[Dict]) -> float:
        """
        Calculate traffic consistency across patterns (0-100)
        100 = very consistent, 0 = highly variable
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
                    if day in pattern and len(pattern[day]) > hour:
                        values.append(pattern[day][hour])
                
                if len(values) > 1:
                    stdev = statistics.stdev(values)
                    all_stdevs.append(stdev)
        
        if not all_stdevs:
            return 50.0
        
        # Lower standard deviation = higher consistency
        avg_stdev = statistics.mean(all_stdevs)
        
        # Convert to 0-100 score (inverse relationship)
        consistency = max(0, 100 - (avg_stdev * 2))
        
        return round(consistency, 2)
    
    def _generate_traffic_insights(self, analysis: Dict) -> str:
        """
        Generate human-readable insights from traffic analysis
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
        if analysis['peak_day'] and analysis['peak_hour'] is not None:
            hour_12 = analysis['peak_hour'] % 12 or 12
            ampm = "AM" if analysis['peak_hour'] < 12 else "PM"
            insights.append(
                f"Peak traffic: {analysis['peak_day']}s at {hour_12}:00 {ampm} "
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


def test_analyzer():
    """
    Test function for development
    """
    import os
    
    db_url = os.getenv('DATABASE_URL')
    
    if not db_url:
        print("Missing DATABASE_URL environment variable")
        return
    
    try:
        db_conn = psycopg2.connect(db_url)
        analyzer = TrafficAnalyzer(db_conn)
        
        print("\n=== Testing Traffic Analyzer ===\n")
        print("Analyzing area traffic for Times Square, NYC...")
        
        analysis = analyzer.analyze_area_traffic(
            latitude=40.7589,
            longitude=-73.9851,
            radius_meters=300
        )
        
        print(f"\nAnalysis Results:")
        print(f"  Locations sampled: {analysis.get('total_locations_sampled', 0)}")
        print(f"  Vitality score: {analysis.get('area_vitality_score', 0)}/100")
        print(f"  Peak: {analysis.get('peak_day', 'N/A')} at {analysis.get('peak_hour', 0)}:00")
        
        if analysis.get('dominant_place_types'):
            print(f"  Dominant types: {analysis['dominant_place_types']}")
        
        db_conn.close()
        print("\n=== Test Complete ===\n")
        
    except Exception as e:
        print(f"Test failed: {str(e)}")


if __name__ == "__main__":
    test_analyzer()
