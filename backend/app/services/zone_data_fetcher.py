"""
Zone Data Fetcher Service

Fetches real data for each optimal zone candidate:
- Demographics from Census API or estimates
- Competitors from SerpAPI
- Foot traffic from our traffic analyzer
- Drive-by traffic estimates
"""

import math
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


@dataclass
class ZoneMetrics:
    """7 key metrics for zone scoring"""
    total_population: int = 0
    population_growth: float = 0.0
    median_income: int = 0
    median_age: float = 0.0
    total_competitors: int = 0
    drive_by_traffic_monthly: int = 0
    foot_traffic_monthly: int = 0
    
    raw_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.raw_data is None:
            self.raw_data = {}


class ZoneDataFetcher:
    """Fetches real data for zone analysis"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def fetch_zone_metrics(
        self,
        center_lat: float,
        center_lng: float,
        radius_miles: float = 3.0,
        business_type: str = None,
        fetch_competitors: bool = True,
        fetch_traffic: bool = True
    ) -> ZoneMetrics:
        """
        Fetch all 7 metrics for a zone
        
        Args:
            center_lat, center_lng: Zone center coordinates
            radius_miles: Zone radius (default 3 miles)
            business_type: Type of business for competitor search
            fetch_competitors: Whether to fetch competitor data
            fetch_traffic: Whether to fetch traffic data
        """
        metrics = ZoneMetrics()
        metrics.raw_data = {
            'center': {'lat': center_lat, 'lng': center_lng},
            'radius_miles': radius_miles
        }
        
        demographics = self._fetch_demographics(center_lat, center_lng, radius_miles)
        metrics.total_population = demographics.get('population', 0)
        metrics.population_growth = demographics.get('growth_rate', 0.0)
        metrics.median_income = demographics.get('median_income', 0)
        metrics.median_age = demographics.get('median_age', 0.0)
        metrics.raw_data['demographics'] = demographics
        
        if fetch_competitors and business_type:
            competitors = self._fetch_competitors(center_lat, center_lng, radius_miles, business_type)
            metrics.total_competitors = competitors.get('count', 0)
            metrics.raw_data['competitors'] = competitors
        
        if fetch_traffic:
            traffic = self._fetch_traffic(center_lat, center_lng, radius_miles)
            metrics.foot_traffic_monthly = traffic.get('foot_traffic_monthly', 0)
            metrics.drive_by_traffic_monthly = traffic.get('drive_by_traffic_monthly', 0)
            metrics.raw_data['traffic'] = traffic
        
        # Calculate trend indicators
        try:
            from app.services.trend_indicators import calculate_trends
            trends = calculate_trends(
                self.db,
                center_lat,
                center_lng,
                radius_miles,
                metrics.raw_data
            )
            metrics.raw_data['trends'] = trends
        except Exception as e:
            logger.warning(f"Failed to calculate trends: {e}")
            metrics.raw_data['trends'] = None
        
        return metrics
    
    def _fetch_demographics(
        self,
        lat: float,
        lng: float,
        radius_miles: float
    ) -> Dict[str, Any]:
        """
        Fetch demographics for an area using deterministic estimates based on location
        
        Uses lat/lng as seed for consistent results across requests
        Each unique coordinate pair generates unique demographic values
        """
        import hashlib
        
        # Use higher precision (6 decimals) for more variation between nearby zones
        seed_str = f"{lat:.6f},{lng:.6f}"
        seed = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
        # Secondary seed for additional variation
        seed2 = int(hashlib.md5(seed_str.encode()).hexdigest()[8:16], 16)
        
        area_sq_miles = math.pi * (radius_miles ** 2)
        
        # Get base density from nearest urban center
        base_density = self._estimate_population_density(lat, lng)
        
        # Apply location-specific variation (±25%) based on seed
        # This ensures each zone gets unique population even in same metro area
        density_variation = 0.75 + ((seed % 500) / 1000.0)  # 0.75 to 1.25
        adjusted_density = base_density * density_variation
        population = int(area_sq_miles * adjusted_density)
        
        # Income varies based on both region and micro-location
        region_factor = self._get_region_income_factor(lat, lng)
        income_base = 45000 + (seed % 40000)  # Base: 45K-85K
        income_micro_adjust = 0.85 + ((seed2 % 300) / 1000.0)  # ±15% micro variation
        median_income = int(income_base * region_factor * income_micro_adjust)
        
        # Median age varies by location characteristics
        age_base = 28 + ((seed >> 8) % 18)  # 28-46 range
        age_micro_adjust = ((seed2 >> 8) % 60) / 10.0 - 3.0  # ±3 years
        median_age = round(age_base + age_micro_adjust + (region_factor - 1) * 2, 1)
        median_age = max(25.0, min(55.0, median_age))  # Clamp to realistic range
        
        # Growth rate varies significantly by micro-location
        growth_base = ((seed >> 16) % 60) / 10.0 - 1.5  # -1.5% to +4.5%
        growth_micro = ((seed2 >> 16) % 20) / 10.0 - 1.0  # ±1% micro variation  
        growth_rate = round(growth_base + growth_micro, 1)
        growth_rate = max(-3.0, min(6.0, growth_rate))  # Clamp to realistic range
        
        # Employment rate varies by location (typically 55-70%)
        employment_base = 60 + ((seed >> 20) % 15) - 2
        employment_micro = ((seed2 >> 20) % 6) - 3
        employment_rate = round(employment_base + employment_micro, 1)
        employment_rate = max(50.0, min(75.0, employment_rate))
        
        return {
            'population': population,
            'median_income': median_income,
            'median_age': median_age,
            'growth_rate': growth_rate,
            'employment_rate': employment_rate,
            'households': int(population / 2.5),
            'area_sq_miles': round(area_sq_miles, 2),
            'source': 'estimated'
        }
    
    def _estimate_population_density(self, lat: float, lng: float) -> int:
        """Estimate population density based on location"""
        urban_centers = [
            (40.7128, -74.0060, 25000),
            (34.0522, -118.2437, 8000),
            (41.8781, -87.6298, 12000),
            (29.7604, -95.3698, 4000),
            (33.4484, -112.0740, 3500),
            (29.4241, -98.4936, 3200),
            (32.7767, -96.7970, 3800),
            (37.7749, -122.4194, 17000),
            (30.2672, -97.7431, 3000),
            (39.7392, -104.9903, 4500),
            (47.6062, -122.3321, 8000),
            (38.9072, -77.0369, 10000),
            (25.7617, -80.1918, 12000),
            (33.7490, -84.3880, 3500),
        ]
        
        min_distance = float('inf')
        nearest_density = 2500
        
        for city_lat, city_lng, density in urban_centers:
            distance = self._haversine(lat, lng, city_lat, city_lng)
            if distance < min_distance:
                min_distance = distance
                nearest_density = density
        
        if min_distance < 10:
            return nearest_density
        elif min_distance < 25:
            return int(nearest_density * 0.6)
        elif min_distance < 50:
            return int(nearest_density * 0.3)
        else:
            return 1500
    
    def _get_region_income_factor(self, lat: float, lng: float) -> float:
        """Get income adjustment factor by region"""
        if lng < -120:
            return 1.25
        elif lng > -75:
            return 1.15
        elif lat > 40:
            return 1.1
        else:
            return 1.0
    
    def _fetch_competitors(
        self,
        lat: float,
        lng: float,
        radius_miles: float,
        business_type: str
    ) -> Dict[str, Any]:
        """
        Fetch competitor data using SerpAPI
        """
        try:
            from app.services.serpapi_service import SerpAPIService
            
            serpapi = SerpAPIService()
            if not serpapi.is_configured:
                return self._estimate_competitors(lat, lng, radius_miles, business_type)
            
            zoom = max(10, min(15, int(14 - math.log2(max(0.5, radius_miles)))))
            ll = f"@{lat},{lng},{zoom}z"
            
            search_query = business_type.replace("_", " ")
            
            result = serpapi.google_maps_search(
                query=search_query,
                ll=ll
            )
            
            local_results = result.get("local_results", [])
            
            filtered = []
            for place in local_results:
                place_lat = place.get("gps_coordinates", {}).get("latitude")
                place_lng = place.get("gps_coordinates", {}).get("longitude")
                
                if place_lat and place_lng:
                    distance = self._haversine(lat, lng, place_lat, place_lng)
                    if distance <= radius_miles:
                        filtered.append({
                            'name': place.get('title', ''),
                            'rating': place.get('rating', 0),
                            'reviews': place.get('reviews', 0),
                            'address': place.get('address', ''),
                            'distance_miles': round(distance, 2)
                        })
            
            area_sq_miles = math.pi * (radius_miles ** 2)
            density = len(filtered) / max(0.1, area_sq_miles)
            return {
                'count': len(filtered),
                'density_per_sq_mile': round(density, 2),
                'competitors': filtered[:10],
                'avg_rating': round(sum(c.get('rating', 0) for c in filtered) / max(1, len(filtered)), 1),
                'source': 'serpapi'
            }
            
        except Exception as e:
            logger.warning(f"Failed to fetch competitors: {e}")
            return self._estimate_competitors(lat, lng, radius_miles, business_type)
    
    def _estimate_competitors(
        self,
        lat: float,
        lng: float,
        radius_miles: float,
        business_type: str
    ) -> Dict[str, Any]:
        """Estimate competitor count when API unavailable - deterministic based on location"""
        import hashlib
        
        # Use location + business type for deterministic variation
        seed_str = f"{lat:.6f},{lng:.6f},{business_type}"
        seed = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
        
        density = self._estimate_population_density(lat, lng)
        
        base_counts = {
            'restaurant': (8, 25),
            'fast_food': (5, 15),
            'cafe': (4, 18),
            'coffee': (3, 12),
            'gym': (2, 8),
            'fitness': (2, 8),
            'self_storage': (1, 6),
            'storage': (1, 6),
            'laundromat': (1, 5),
            'retail': (10, 30),
            'salon': (5, 15),
        }
        
        normalized = business_type.lower().replace(" ", "_").replace("-", "_")
        min_count, max_count = base_counts.get(normalized, (3, 15))
        
        # Deterministic count based on seed
        range_size = max_count - min_count
        base_count = min_count + (seed % (range_size + 1))
        
        density_factor = density / 5000
        count = int(base_count * density_factor)
        count = max(0, min(count, max_count * 2))
        
        # Deterministic rating
        rating = 3.5 + ((seed >> 8) % 10) / 10.0  # 3.5 to 4.4
        
        # Calculate density per sq mile
        area_sq_miles = math.pi * (radius_miles ** 2)
        competitor_density = count / max(0.1, area_sq_miles)
        
        return {
            'count': count,
            'density_per_sq_mile': round(competitor_density, 2),
            'competitors': [],
            'avg_rating': round(rating, 1),
            'source': 'estimated'
        }
    
    def _fetch_traffic(
        self,
        lat: float,
        lng: float,
        radius_miles: float
    ) -> Dict[str, Any]:
        """
        Fetch traffic data using fusion of multiple sources:
        - Google Popular Times (foot traffic, real-time activity)
        - DOT AADT (vehicle traffic, official data)
        
        The fusion algorithm combines both for more accurate estimates.
        """
        google_data = None
        dot_data = None
        
        # Get Google Popular Times data (foot traffic)
        try:
            from app.services.traffic_analyzer import TrafficAnalyzer
            
            analyzer = TrafficAnalyzer(self.db)
            radius_meters = int(radius_miles * 1609.34)
            google_data = analyzer.analyze_area_traffic(lat, lng, radius_meters)
        except Exception as e:
            logger.debug(f"Google traffic lookup failed: {e}")
        
        # Get DOT AADT data (vehicle traffic)
        try:
            from app.services.dot_traffic_service import DOTTrafficService
            dot_service = DOTTrafficService(timeout=5)
            dot_data = dot_service.get_area_traffic_summary(lat, lng, radius_miles)
        except Exception as e:
            logger.debug(f"DOT traffic lookup failed: {e}")
        
        # Fuse the data sources
        try:
            from app.services.traffic_fusion import fuse_traffic
            
            fused = fuse_traffic(lat, lng, radius_miles, dot_data, google_data)
            
            return {
                'foot_traffic_monthly': fused.monthly_foot_traffic,
                'drive_by_traffic_monthly': fused.monthly_vehicle_traffic,
                'vitality_score': google_data.get('area_vitality_score', 0) if google_data else 0,
                'peak_day': google_data.get('peak_day') if google_data else None,
                'peak_hour': google_data.get('peak_hour') if google_data else None,
                'locations_sampled': google_data.get('total_locations_sampled', 0) if google_data else 0,
                'source': fused.primary_source,
                'confidence': fused.confidence_score,
                'fusion_breakdown': fused.breakdown
            }
            
        except Exception as e:
            logger.warning(f"Traffic fusion failed, using fallback: {e}")
            return self._estimate_traffic(lat, lng, radius_miles)
    
    def _estimate_drive_by_traffic(
        self,
        lat: float,
        lng: float,
        radius_miles: float,
        foot_traffic_data: Dict
    ) -> int:
        """
        Get drive-by traffic from DOT data when available, otherwise estimate.
        
        First tries to fetch real AADT data from state DOT ArcGIS services.
        Falls back to estimation based on foot traffic and area characteristics.
        """
        # Try DOT API first
        try:
            from app.services.dot_traffic_service import DOTTrafficService
            dot_service = DOTTrafficService(timeout=5)
            dot_result = dot_service.get_area_traffic_summary(lat, lng, radius_miles)
            
            if dot_result.get('source') in ('dot_api', 'local_db') and dot_result.get('monthly_estimate', 0) > 0:
                logger.info(f"Got DOT traffic data for {lat}, {lng}: {dot_result['monthly_estimate']}/mo")
                return dot_result['monthly_estimate']
        except Exception as e:
            logger.debug(f"DOT traffic lookup failed, using estimate: {e}")
        
        # Fall back to estimation
        foot_traffic = foot_traffic_data.get('avg_daily_traffic', 0)
        vitality = foot_traffic_data.get('area_vitality_score', 50)
        
        density = self._estimate_population_density(lat, lng)
        
        if density > 10000:
            vehicle_ratio = 3.0
        elif density > 5000:
            vehicle_ratio = 5.0
        else:
            vehicle_ratio = 8.0
        
        if foot_traffic > 0:
            daily_vehicles = foot_traffic * vehicle_ratio
        else:
            daily_vehicles = (vitality / 100) * density * 0.5
        
        monthly_traffic = int(daily_vehicles * 30)
        
        return max(0, monthly_traffic)
    
    def _estimate_traffic(
        self,
        lat: float,
        lng: float,
        radius_miles: float
    ) -> Dict[str, Any]:
        """Estimate traffic when no data available - deterministic based on location"""
        import hashlib
        
        # Deterministic seed based on location
        seed_str = f"{lat:.6f},{lng:.6f}"
        seed = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
        seed2 = int(hashlib.md5(seed_str.encode()).hexdigest()[8:16], 16)
        
        density = self._estimate_population_density(lat, lng)
        
        # Deterministic variation factors
        foot_variation = 0.8 + ((seed % 400) / 1000.0)  # 0.8 to 1.2
        drive_variation = 4.0 + ((seed2 % 400) / 100.0)  # 4.0 to 8.0
        
        foot_traffic_daily = int(density * 0.05 * foot_variation)
        drive_by_daily = int(foot_traffic_daily * drive_variation)
        
        return {
            'foot_traffic_monthly': foot_traffic_daily * 30,
            'drive_by_traffic_monthly': drive_by_daily * 30,
            'vitality_score': min(100, int(density / 100)),
            'peak_day': None,
            'peak_hour': None,
            'locations_sampled': 0,
            'source': 'estimated'
        }
    
    @staticmethod
    def _haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance in miles between two coordinates"""
        R = 3959
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c


def calculate_zone_score(metrics: ZoneMetrics, weights: Dict[str, float] = None) -> Dict[str, Any]:
    """
    Calculate zone score using derived metrics for better comparability
    
    Uses derived metrics calculator for normalized scoring.
    Returns both raw component scores and derived metrics.
    """
    from app.services.derived_metrics import calculate_derived_metrics
    
    derived = calculate_derived_metrics(
        total_population=metrics.total_population,
        population_growth=metrics.population_growth,
        median_income=metrics.median_income,
        median_age=metrics.median_age,
        total_competitors=metrics.total_competitors,
        foot_traffic_monthly=metrics.foot_traffic_monthly,
        drive_by_traffic_monthly=metrics.drive_by_traffic_monthly
    )
    
    if weights is None:
        weights = {
            'population': 0.10,
            'growth': 0.10,
            'income': 0.10,
            'age': 0.10,
            'competition': 0.20,
            'foot_traffic': 0.20,
            'drive_by_traffic': 0.20
        }
    
    scores = {}
    
    pop = metrics.total_population
    if pop >= 100000:
        scores['population'] = 100
    elif pop >= 50000:
        scores['population'] = 80
    elif pop >= 25000:
        scores['population'] = 60
    elif pop >= 10000:
        scores['population'] = 40
    else:
        scores['population'] = max(20, pop / 500)
    
    growth = metrics.population_growth
    if growth >= 3.0:
        scores['growth'] = 100
    elif growth >= 2.0:
        scores['growth'] = 80
    elif growth >= 1.0:
        scores['growth'] = 60
    elif growth >= 0:
        scores['growth'] = 40
    else:
        scores['growth'] = max(10, 40 + growth * 10)
    
    income = metrics.median_income
    if income >= 100000:
        scores['income'] = 100
    elif income >= 75000:
        scores['income'] = 80
    elif income >= 55000:
        scores['income'] = 60
    elif income >= 40000:
        scores['income'] = 40
    else:
        scores['income'] = max(20, income / 2000)
    
    age = metrics.median_age
    if 30 <= age <= 45:
        scores['age'] = 100
    elif 25 <= age < 30 or 45 < age <= 50:
        scores['age'] = 80
    elif 22 <= age < 25 or 50 < age <= 55:
        scores['age'] = 60
    else:
        scores['age'] = 40
    
    comps = metrics.total_competitors
    if comps == 0:
        scores['competition'] = 40
    elif 1 <= comps <= 3:
        scores['competition'] = 100
    elif 4 <= comps <= 6:
        scores['competition'] = 80
    elif 7 <= comps <= 10:
        scores['competition'] = 60
    elif 11 <= comps <= 15:
        scores['competition'] = 40
    else:
        scores['competition'] = max(10, 40 - (comps - 15) * 2)
    
    foot = metrics.foot_traffic_monthly
    if foot >= 50000:
        scores['foot_traffic'] = 100
    elif foot >= 25000:
        scores['foot_traffic'] = 80
    elif foot >= 10000:
        scores['foot_traffic'] = 60
    elif foot >= 5000:
        scores['foot_traffic'] = 40
    else:
        scores['foot_traffic'] = max(20, foot / 250)
    
    drive = metrics.drive_by_traffic_monthly
    if drive >= 200000:
        scores['drive_by_traffic'] = 100
    elif drive >= 100000:
        scores['drive_by_traffic'] = 80
    elif drive >= 50000:
        scores['drive_by_traffic'] = 60
    elif drive >= 20000:
        scores['drive_by_traffic'] = 40
    else:
        scores['drive_by_traffic'] = max(20, drive / 1000)
    
    total_score = derived.overall_score
    
    return {
        'total_score': round(total_score, 1),
        'component_scores': {k: round(v, 1) for k, v in scores.items()},
        'weights': weights,
        'derived_metrics': derived.to_dict(),
        'category_scores': derived.category_scores
    }
