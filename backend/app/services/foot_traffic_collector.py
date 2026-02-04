"""
OppGrid Foot Traffic Data Collector
Extracts Google Maps Popular Times data using SerpAPI

Usage:
    from app.services.foot_traffic_collector import FootTrafficCollector
    
    collector = FootTrafficCollector(db_session)
    traffic_data = collector.get_area_traffic(lat, lng, radius_miles=0.5)
    collector.save_traffic_data(traffic_data)
"""

import os
import requests
import time
from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

SERPAPI_KEY = os.getenv('SERPAPI_KEY')
SERPAPI_BASE_URL = "https://serpapi.com/search.json"


class FootTrafficCollector:
    """
    Collects foot traffic data from Google Maps Popular Times via SerpAPI
    """
    
    def __init__(self, db: Session):
        """
        Initialize collector with database session
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.api_key = SERPAPI_KEY
        if not self.api_key:
            logger.warning("SERPAPI_KEY not configured - foot traffic collection will fail")
    
    def get_place_traffic(self, place_id: str) -> Optional[Dict]:
        """
        Get foot traffic data for a specific Google Place ID using SerpAPI Place Results
        
        Args:
            place_id: Google Maps Place ID
            
        Returns:
            Dictionary with traffic data or None if unavailable
        """
        if not self.api_key:
            logger.error("SERPAPI_KEY not configured")
            return None
            
        try:
            params = {
                "engine": "google_maps",
                "place_id": place_id,
                "api_key": self.api_key
            }
            
            response = requests.get(SERPAPI_BASE_URL, params=params, timeout=30)
            
            if response.status_code != 200:
                logger.warning(f"SerpAPI request failed for place {place_id}: {response.status_code}")
                return None
            
            data = response.json()
            place_results = data.get("place_results", {})
            
            if not place_results:
                logger.info(f"No place results for {place_id}")
                return None
            
            gps = place_results.get("gps_coordinates", {})
            popular_times_raw = place_results.get("popular_times", {})
            
            popular_times = self._format_popular_times(popular_times_raw)
            
            traffic_info = {
                'place_id': place_id,
                'place_name': place_results.get('title', 'Unknown'),
                'place_address': place_results.get('address', ''),
                'place_type': place_results.get('type', 'business'),
                'latitude': gps.get('latitude'),
                'longitude': gps.get('longitude'),
                'popular_times': popular_times,
                'current_popularity': self._get_current_popularity(popular_times_raw),
                'time_spent': place_results.get('typical_time_spent'),
                'data_quality_score': self._calculate_data_quality(popular_times, place_results)
            }
            
            if traffic_info['latitude'] and traffic_info['longitude']:
                logger.info(f"Successfully collected traffic for {traffic_info['place_name']}")
                return traffic_info
            
            return None
            
        except Exception as e:
            logger.error(f"Error collecting traffic for place {place_id}: {str(e)}")
            return None
    
    def search_nearby_places(self, latitude: float, longitude: float, 
                             query: str = "business",
                             radius_miles: float = 0.5) -> List[Dict]:
        """
        Search for nearby places using SerpAPI Google Maps Local Results
        
        Args:
            latitude: Center point latitude
            longitude: Center point longitude
            query: Search query (e.g., "restaurant", "store")
            radius_miles: Search radius in miles
            
        Returns:
            List of place dictionaries with place_id
        """
        if not self.api_key:
            logger.error("SERPAPI_KEY not configured")
            return []
            
        try:
            ll = f"@{latitude},{longitude},14z"
            
            params = {
                "engine": "google_maps",
                "q": query,
                "ll": ll,
                "type": "search",
                "api_key": self.api_key
            }
            
            response = requests.get(SERPAPI_BASE_URL, params=params, timeout=30)
            
            if response.status_code != 200:
                logger.warning(f"SerpAPI search failed: {response.status_code}")
                return []
            
            data = response.json()
            local_results = data.get("local_results", [])
            
            places = []
            for result in local_results:
                place_id = result.get("place_id")
                if place_id:
                    places.append({
                        "place_id": place_id,
                        "name": result.get("title", ""),
                        "address": result.get("address", ""),
                        "type": result.get("type", ""),
                        "rating": result.get("rating"),
                        "reviews": result.get("reviews"),
                        "gps_coordinates": result.get("gps_coordinates", {})
                    })
            
            logger.info(f"Found {len(places)} places for query '{query}' near ({latitude}, {longitude})")
            return places
            
        except Exception as e:
            logger.error(f"Error searching nearby places: {str(e)}")
            return []
    
    def get_area_traffic(self, latitude: float, longitude: float, 
                         radius_miles: float = 0.5,
                         place_types: List[str] = None,
                         max_places: int = 20) -> List[Dict]:
        """
        Get foot traffic data for all relevant places in an area
        
        Args:
            latitude: Center point latitude
            longitude: Center point longitude
            radius_miles: Search radius in miles
            place_types: Filter by place types (e.g., ['restaurant', 'store'])
            max_places: Maximum number of places to collect
            
        Returns:
            List of traffic data dictionaries
        """
        if place_types is None:
            place_types = [
                'restaurant', 'cafe', 'store', 'shopping',
                'gym', 'bar', 'supermarket', 'retail'
            ]
        
        logger.info(f"Collecting area traffic at ({latitude}, {longitude}) radius {radius_miles}mi")
        
        all_traffic_data = []
        seen_place_ids = set()
        
        for place_type in place_types:
            if len(all_traffic_data) >= max_places:
                break
                
            try:
                places = self.search_nearby_places(
                    latitude, longitude, 
                    query=place_type,
                    radius_miles=radius_miles
                )
                
                for place in places:
                    if len(all_traffic_data) >= max_places:
                        break
                        
                    place_id = place.get('place_id')
                    if not place_id or place_id in seen_place_ids:
                        continue
                    
                    seen_place_ids.add(place_id)
                    
                    time.sleep(0.2)
                    
                    traffic_data = self.get_place_traffic(place_id)
                    if traffic_data and traffic_data.get('popular_times'):
                        all_traffic_data.append(traffic_data)
                
                time.sleep(0.3)
                
            except Exception as e:
                logger.error(f"Error processing place type {place_type}: {str(e)}")
                continue
        
        logger.info(f"Collected traffic data for {len(all_traffic_data)} locations")
        return all_traffic_data
    
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
        
        saved_count = 0
        
        for data in traffic_data:
            try:
                import json
                popular_times_json = json.dumps(data.get('popular_times')) if data.get('popular_times') else None
                
                time_spent = data.get('time_spent')
                time_spent_min = None
                time_spent_max = None
                if time_spent and isinstance(time_spent, str):
                    parts = time_spent.replace('min', '').replace('hr', '').split('-')
                    if len(parts) >= 1:
                        try:
                            time_spent_min = int(parts[0].strip())
                        except:
                            pass
                    if len(parts) >= 2:
                        try:
                            time_spent_max = int(parts[1].strip())
                        except:
                            pass
                
                query = text("""
                INSERT INTO foot_traffic (
                    place_id, place_name, place_address, place_type,
                    latitude, longitude, location,
                    popular_times, current_popularity,
                    time_spent_min, time_spent_max,
                    data_quality_score, last_updated
                )
                VALUES (
                    :place_id, :place_name, :place_address, :place_type,
                    :latitude, :longitude, ST_MakePoint(:longitude, :latitude)::geography,
                    CAST(:popular_times AS jsonb), :current_popularity,
                    :time_spent_min, :time_spent_max,
                    :data_quality_score, NOW()
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
                """)
                
                self.db.execute(query, {
                    'place_id': data['place_id'],
                    'place_name': data['place_name'],
                    'place_address': data['place_address'],
                    'place_type': data['place_type'],
                    'latitude': data['latitude'],
                    'longitude': data['longitude'],
                    'popular_times': popular_times_json,
                    'current_popularity': data.get('current_popularity'),
                    'time_spent_min': time_spent_min,
                    'time_spent_max': time_spent_max,
                    'data_quality_score': data.get('data_quality_score', 0.7)
                })
                saved_count += 1
                
            except Exception as e:
                logger.error(f"Error saving traffic data for {data.get('place_id', 'unknown')}: {str(e)}")
                continue
        
        self.db.commit()
        logger.info(f"Successfully saved {saved_count} traffic records")
        return saved_count
    
    def _format_popular_times(self, popular_times_raw: Dict) -> Dict:
        """
        Format SerpAPI popular times data into consistent structure
        
        Args:
            popular_times_raw: Raw popular times from SerpAPI
            
        Returns:
            Formatted dictionary with day names as keys and 24-hour arrays
        """
        if not popular_times_raw:
            return {}
        
        graph_results = popular_times_raw.get('graph_results', {})
        if not graph_results:
            return {}
        
        days_map = {
            'sunday': 'Sunday',
            'monday': 'Monday',
            'tuesday': 'Tuesday',
            'wednesday': 'Wednesday',
            'thursday': 'Thursday',
            'friday': 'Friday',
            'saturday': 'Saturday'
        }
        
        formatted = {}
        
        for day_key, day_name in days_map.items():
            day_data = graph_results.get(day_key, [])
            
            hourly_values = [0] * 24
            
            for entry in day_data:
                time_str = entry.get('time', '')
                busyness = entry.get('busyness_score', 0)
                
                hour = self._parse_time_to_hour(time_str)
                if hour is not None and 0 <= hour < 24:
                    hourly_values[hour] = busyness
            
            formatted[day_name] = hourly_values
        
        return formatted
    
    def _parse_time_to_hour(self, time_str: str) -> Optional[int]:
        """Parse time string like '10 AM' or '2 PM' to 24-hour format"""
        if not time_str:
            return None
        
        try:
            time_str = time_str.strip().upper()
            parts = time_str.replace('AM', '').replace('PM', '').strip().split(':')
            hour = int(parts[0])
            
            if 'PM' in time_str and hour != 12:
                hour += 12
            elif 'AM' in time_str and hour == 12:
                hour = 0
            
            return hour
        except:
            return None
    
    def _get_current_popularity(self, popular_times_raw: Dict) -> Optional[int]:
        """Extract current popularity if available"""
        if not popular_times_raw:
            return None
        
        live_busyness = popular_times_raw.get('live_busyness', {})
        if live_busyness:
            return live_busyness.get('current_popularity')
        
        return None
    
    def _calculate_data_quality(self, popular_times: Dict, place_results: Dict) -> float:
        """
        Calculate data quality score based on completeness
        
        Returns:
            Quality score 0.0-1.0
        """
        score = 0.0
        
        if popular_times:
            days_with_data = sum(1 for day in popular_times.values() if any(v > 0 for v in day))
            score += (days_with_data / 7.0) * 0.5
        
        if place_results.get('reviews'):
            score += 0.2
        
        if place_results.get('rating'):
            score += 0.1
        
        if place_results.get('address'):
            score += 0.1
        
        if place_results.get('hours'):
            score += 0.1
        
        return min(score, 1.0)


def check_cached_traffic(db: Session, latitude: float, longitude: float, 
                         radius_meters: int = 800, max_age_days: int = 7) -> Optional[Dict]:
    """
    Check if we have recent cached traffic data for this area
    
    Args:
        db: Database session
        latitude: Center latitude
        longitude: Center longitude
        radius_meters: Search radius
        max_age_days: Maximum age of cached data
        
    Returns:
        Cached aggregation if available, None otherwise
    """
    try:
        query = text("""
        SELECT 
            id, area_name, avg_popular_times, total_locations_sampled,
            dominant_place_types, peak_day, peak_hour, peak_traffic_score,
            area_vitality_score, business_density_score, foot_traffic_consistency,
            last_refreshed
        FROM area_traffic_aggregations
        WHERE ST_DWithin(
            center_location,
            ST_MakePoint(:lng, :lat)::geography,
            :radius
        )
        AND last_refreshed > NOW() - INTERVAL ':days days'
        ORDER BY last_refreshed DESC
        LIMIT 1
        """)
        
        result = db.execute(query, {
            'lat': latitude,
            'lng': longitude,
            'radius': radius_meters,
            'days': max_age_days
        }).fetchone()
        
        if result:
            return {
                'id': result[0],
                'area_name': result[1],
                'avg_popular_times': result[2],
                'total_locations_sampled': result[3],
                'dominant_place_types': result[4],
                'peak_day': result[5],
                'peak_hour': result[6],
                'peak_traffic_score': result[7],
                'area_vitality_score': float(result[8]) if result[8] else None,
                'business_density_score': float(result[9]) if result[9] else None,
                'foot_traffic_consistency': float(result[10]) if result[10] else None,
                'last_refreshed': result[11].isoformat() if result[11] else None
            }
        
        return None
        
    except Exception as e:
        logger.error(f"Error checking cached traffic: {str(e)}")
        return None
