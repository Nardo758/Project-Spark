"""
DOT Traffic Data Service

Fetches Annual Average Daily Traffic (AADT) data from state DOT ArcGIS services.
Falls back to estimates when API data is unavailable.

State DOT ArcGIS endpoints vary - this service maintains a registry of known endpoints
and queries the appropriate one based on coordinates.
"""

import requests
import logging
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass
import math

logger = logging.getLogger(__name__)

# State DOT ArcGIS REST API endpoints that provide AADT data
# Format: state_code -> (base_url, layer_id, aadt_field_name)
STATE_DOT_ENDPOINTS = {
    'WV': {
        'url': 'https://gis.transportation.wv.gov/arcgis/rest/services/Projects/AADT/FeatureServer/0',
        'aadt_field': 'AADT',
        'route_field': 'ROUTE',
    },
    'MD': {
        'url': 'https://services.arcgis.com/njFNhDsUCentVYJW/arcgis/rest/services/MDOT_SHA_Annual_Average_Daily_Traffic_AADT/FeatureServer/0',
        'aadt_field': 'AADT',
        'route_field': 'ROUTE_ID',
    },
    'VA': {
        'url': 'https://services3.arcgis.com/xGhcsq2HSmrbR1q5/arcgis/rest/services/AADT/FeatureServer/0',
        'aadt_field': 'AADT',
        'route_field': 'RTE_NM',
    },
    'NC': {
        'url': 'https://services.arcgis.com/AeiMNsJpVhQRH3rz/arcgis/rest/services/NCDOT_AADT/FeatureServer/0',
        'aadt_field': 'AADT',
        'route_field': 'ROUTE',
    },
    'TX': {
        'url': 'https://services.arcgis.com/KTcxiTD9dsQw4r7Z/arcgis/rest/services/TxDOT_AADT/FeatureServer/0',
        'aadt_field': 'AADT',
        'route_field': 'RTE_NM',
    },
    'CA': {
        'url': 'https://services.arcgis.com/VUdK2N9n7S8yUQkV/arcgis/rest/services/Traffic_Volumes_AADT/FeatureServer/0',
        'aadt_field': 'AADT',
        'route_field': 'ROUTE',
    },
    'FL': {
        'url': 'https://services1.arcgis.com/O1JpcwDW8sjYuddV/arcgis/rest/services/AADT_On_The_SHS/FeatureServer/0',
        'aadt_field': 'APTS_AADT',
        'route_field': 'ROAD_NAME',
    },
    'GA': {
        'url': 'https://services1.arcgis.com/d3bNBZwPpNmxmElo/arcgis/rest/services/GDOT_Traffic_Counts/FeatureServer/0',
        'aadt_field': 'AADT',
        'route_field': 'ROUTE_ID',
    },
    'NY': {
        'url': 'https://services6.arcgis.com/DZHaqZm9cxOD4CWM/arcgis/rest/services/NYSDOT_Traffic_Counts/FeatureServer/0',
        'aadt_field': 'AADT',
        'route_field': 'ROUTE',
    },
}

# State bounding boxes for coordinate-to-state lookup (approximate)
STATE_BOUNDS = {
    'WV': {'min_lat': 37.2, 'max_lat': 40.6, 'min_lng': -82.6, 'max_lng': -77.7},
    'MD': {'min_lat': 37.9, 'max_lat': 39.7, 'min_lng': -79.5, 'max_lng': -75.0},
    'VA': {'min_lat': 36.5, 'max_lat': 39.5, 'min_lng': -83.7, 'max_lng': -75.2},
    'NC': {'min_lat': 33.8, 'max_lat': 36.6, 'min_lng': -84.3, 'max_lng': -75.5},
    'TX': {'min_lat': 25.8, 'max_lat': 36.5, 'min_lng': -106.6, 'max_lng': -93.5},
    'CA': {'min_lat': 32.5, 'max_lat': 42.0, 'min_lng': -124.4, 'max_lng': -114.1},
    'FL': {'min_lat': 24.5, 'max_lat': 31.0, 'min_lng': -87.6, 'max_lng': -80.0},
    'GA': {'min_lat': 30.4, 'max_lat': 35.0, 'min_lng': -85.6, 'max_lng': -80.8},
    'NY': {'min_lat': 40.5, 'max_lat': 45.0, 'min_lng': -79.8, 'max_lng': -71.9},
}


@dataclass
class TrafficDataResult:
    """Result from DOT traffic data query"""
    aadt: int  # Annual Average Daily Traffic
    route_name: Optional[str] = None
    source: str = 'estimated'  # 'dot_api', 'estimated'
    distance_miles: Optional[float] = None  # Distance to nearest road segment
    state: Optional[str] = None
    raw_data: Optional[Dict] = None


class DOTTrafficService:
    """Service to fetch traffic data from DOT sources"""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self._cache: Dict[str, TrafficDataResult] = {}
    
    def get_traffic_for_location(
        self,
        lat: float,
        lng: float,
        radius_miles: float = 1.0
    ) -> TrafficDataResult:
        """
        Get AADT traffic data for a location.
        
        Queries the appropriate state DOT API based on coordinates.
        Falls back to estimates if no API data available.
        
        Args:
            lat: Latitude
            lng: Longitude  
            radius_miles: Search radius for nearby road segments
            
        Returns:
            TrafficDataResult with AADT and metadata
        """
        cache_key = f"{lat:.3f},{lng:.3f},{radius_miles}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        state = self._get_state_from_coords(lat, lng)
        
        if state and state in STATE_DOT_ENDPOINTS:
            result = self._query_state_dot(state, lat, lng, radius_miles)
            if result:
                self._cache[cache_key] = result
                return result
        
        # Fall back to estimate
        result = self._estimate_traffic(lat, lng, radius_miles)
        self._cache[cache_key] = result
        return result
    
    def get_area_traffic_summary(
        self,
        lat: float,
        lng: float,
        radius_miles: float = 3.0,
        sample_points: int = 5
    ) -> Dict[str, Any]:
        """
        Get aggregated traffic data for an area by sampling multiple points.
        
        Args:
            lat: Center latitude
            lng: Center longitude
            radius_miles: Area radius
            sample_points: Number of points to sample
            
        Returns:
            Dictionary with aggregated traffic metrics
        """
        points = self._generate_sample_points(lat, lng, radius_miles, sample_points)
        
        results: List[TrafficDataResult] = []
        for p_lat, p_lng in points:
            result = self.get_traffic_for_location(p_lat, p_lng, 0.5)
            results.append(result)
        
        aadt_values = [r.aadt for r in results if r.aadt > 0]
        api_results = [r for r in results if r.source == 'dot_api']
        
        if not aadt_values:
            return {
                'avg_daily_traffic': 0,
                'max_daily_traffic': 0,
                'min_daily_traffic': 0,
                'monthly_estimate': 0,
                'source': 'no_data',
                'api_coverage_pct': 0,
            }
        
        avg_aadt = sum(aadt_values) / len(aadt_values)
        
        return {
            'avg_daily_traffic': int(avg_aadt),
            'max_daily_traffic': max(aadt_values),
            'min_daily_traffic': min(aadt_values),
            'monthly_estimate': int(avg_aadt * 30),
            'source': 'dot_api' if api_results else 'estimated',
            'api_coverage_pct': round(len(api_results) / len(results) * 100, 1),
            'samples': len(results),
        }
    
    def _get_state_from_coords(self, lat: float, lng: float) -> Optional[str]:
        """Determine which state a coordinate falls in"""
        for state, bounds in STATE_BOUNDS.items():
            if (bounds['min_lat'] <= lat <= bounds['max_lat'] and
                bounds['min_lng'] <= lng <= bounds['max_lng']):
                return state
        return None
    
    def _query_state_dot(
        self,
        state: str,
        lat: float,
        lng: float,
        radius_miles: float
    ) -> Optional[TrafficDataResult]:
        """Query a state DOT ArcGIS service for AADT data"""
        endpoint = STATE_DOT_ENDPOINTS.get(state)
        if not endpoint:
            return None
        
        try:
            # Convert radius to meters for spatial query
            radius_meters = radius_miles * 1609.34
            
            # Build ArcGIS query
            params = {
                'where': '1=1',
                'geometry': f'{lng},{lat}',
                'geometryType': 'esriGeometryPoint',
                'spatialRel': 'esriSpatialRelIntersects',
                'distance': radius_meters,
                'units': 'esriSRUnit_Meter',
                'outFields': '*',
                'returnGeometry': 'false',
                'f': 'json',
                'resultRecordCount': 10,
            }
            
            response = requests.get(
                f"{endpoint['url']}/query",
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            if 'features' not in data or not data['features']:
                logger.debug(f"No features found for {lat}, {lng} in {state}")
                return None
            
            # Get the highest AADT value from nearby segments
            aadt_field = endpoint['aadt_field']
            route_field = endpoint.get('route_field', 'ROUTE')
            
            best_aadt = 0
            best_route = None
            
            for feature in data['features']:
                attrs = feature.get('attributes', {})
                aadt = attrs.get(aadt_field, 0)
                if aadt and aadt > best_aadt:
                    best_aadt = int(aadt)
                    best_route = attrs.get(route_field)
            
            if best_aadt > 0:
                return TrafficDataResult(
                    aadt=best_aadt,
                    route_name=str(best_route) if best_route else None,
                    source='dot_api',
                    state=state,
                    raw_data={'features_found': len(data['features'])}
                )
            
            return None
            
        except requests.RequestException as e:
            logger.warning(f"Failed to query {state} DOT API: {e}")
            return None
        except Exception as e:
            logger.error(f"Error processing {state} DOT response: {e}")
            return None
    
    def _estimate_traffic(
        self,
        lat: float,
        lng: float,
        radius_miles: float
    ) -> TrafficDataResult:
        """
        Estimate AADT based on location characteristics.
        
        Uses population density and urban center proximity as proxies.
        """
        import hashlib
        
        # Use deterministic seed for consistent estimates
        seed_str = f"{lat:.4f},{lng:.4f}"
        seed = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
        
        # Estimate based on urban proximity
        urban_centers = [
            (40.7128, -74.0060, 'NYC', 50000),
            (34.0522, -118.2437, 'LA', 45000),
            (41.8781, -87.6298, 'Chicago', 40000),
            (29.7604, -95.3698, 'Houston', 35000),
            (33.4484, -112.0740, 'Phoenix', 30000),
            (39.7392, -104.9903, 'Denver', 28000),
            (47.6062, -122.3321, 'Seattle', 32000),
            (25.7617, -80.1918, 'Miami', 35000),
            (33.7490, -84.3880, 'Atlanta', 33000),
            (42.3601, -71.0589, 'Boston', 30000),
        ]
        
        min_dist = float('inf')
        base_aadt = 5000
        
        for center_lat, center_lng, name, city_aadt in urban_centers:
            dist = self._haversine(lat, lng, center_lat, center_lng)
            if dist < min_dist:
                min_dist = dist
                # AADT decays with distance from city center
                if dist < 10:
                    base_aadt = city_aadt
                elif dist < 30:
                    base_aadt = int(city_aadt * 0.6)
                elif dist < 60:
                    base_aadt = int(city_aadt * 0.3)
                elif dist < 100:
                    base_aadt = int(city_aadt * 0.15)
                else:
                    base_aadt = int(city_aadt * 0.05)
        
        # Add some variation based on seed
        variation = 0.7 + (seed % 60) / 100  # 0.7 to 1.3
        estimated_aadt = int(base_aadt * variation)
        
        return TrafficDataResult(
            aadt=max(1000, estimated_aadt),
            source='estimated',
            raw_data={'base_aadt': base_aadt, 'nearest_city_dist': round(min_dist, 1)}
        )
    
    def _generate_sample_points(
        self,
        center_lat: float,
        center_lng: float,
        radius_miles: float,
        num_points: int
    ) -> List[Tuple[float, float]]:
        """Generate sample points within a radius"""
        points = [(center_lat, center_lng)]  # Include center
        
        if num_points <= 1:
            return points
        
        # Generate points on concentric rings
        for i in range(num_points - 1):
            angle = (i / (num_points - 1)) * 2 * math.pi
            dist = radius_miles * 0.7  # Sample at 70% of radius
            
            # Convert to lat/lng offset
            delta_lat = (dist / 69) * math.cos(angle)
            delta_lng = (dist / (69 * math.cos(math.radians(center_lat)))) * math.sin(angle)
            
            points.append((center_lat + delta_lat, center_lng + delta_lng))
        
        return points
    
    @staticmethod
    def _haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance in miles between two coordinates"""
        R = 3959  # Earth's radius in miles
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c


# Convenience function
def get_dot_traffic(lat: float, lng: float, radius_miles: float = 3.0) -> Dict[str, Any]:
    """Get DOT traffic data for a location"""
    service = DOTTrafficService()
    return service.get_area_traffic_summary(lat, lng, radius_miles)
