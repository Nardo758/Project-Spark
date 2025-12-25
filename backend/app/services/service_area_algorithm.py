"""
Dynamic Service Area Algorithm

Computes optimal service areas for opportunities using:
1. Signal clustering - Groups nearby opportunity signals
2. Demographic validation - Validates market potential using Census data
3. Geographic boundaries - Creates polygon/radius-based service areas
"""
import math
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.opportunity import Opportunity
from app.models.census_demographics import ServiceAreaBoundary, MarketGrowthTrajectory, GrowthCategory


class ServiceAreaAlgorithm:
    """Computes dynamic service areas for opportunities."""
    
    DEFAULT_RADIUS_MILES = 25
    MIN_RADIUS_MILES = 5
    MAX_RADIUS_MILES = 100
    
    SIGNAL_DENSITY_THRESHOLDS = {
        "high": 10,
        "medium": 5,
        "low": 1
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    def compute_service_area(
        self,
        opportunity: Opportunity,
        demographics: Optional[Dict] = None
    ) -> ServiceAreaBoundary:
        """
        Compute and store a service area for an opportunity.
        
        Args:
            opportunity: The opportunity to compute service area for
            demographics: Optional Census demographics data
            
        Returns:
            ServiceAreaBoundary record
        """
        existing = self.db.query(ServiceAreaBoundary).filter(
            ServiceAreaBoundary.opportunity_id == opportunity.id,
            ServiceAreaBoundary.is_active == True
        ).first()
        
        if existing and existing.computed_at and existing.computed_at.replace(tzinfo=timezone.utc) > datetime.now(timezone.utc) - timedelta(days=7):
            return existing
        
        if existing:
            existing.is_active = False
            self.db.commit()
        
        center_lat = opportunity.latitude
        center_lon = opportunity.longitude
        
        if not center_lat or not center_lon:
            center_lat, center_lon = self._geocode_from_city(opportunity.city, opportunity.region)
        
        if not center_lat or not center_lon:
            center_lat, center_lon = 39.8283, -98.5795
        
        nearby_signals = self._find_nearby_signals(
            str(opportunity.category),
            center_lat,
            center_lon,
            self.MAX_RADIUS_MILES
        )
        
        clusters = self._cluster_signals(nearby_signals, eps_miles=15.0, min_samples=2)
        
        primary_cluster = None
        if clusters:
            clusters_with_dist = []
            for cluster in clusters:
                centroid = self._compute_cluster_centroid(cluster)
                dist = self._distance_miles(center_lat, center_lon, centroid[0], centroid[1])
                clusters_with_dist.append((cluster, dist))
            
            clusters_with_dist.sort(key=lambda x: x[1])
            primary_cluster = clusters_with_dist[0][0]
        
        if primary_cluster and len(primary_cluster) >= 3:
            cluster_points = [(float(s.latitude), float(s.longitude)) for s in primary_cluster]
            geojson_polygon = self._create_convex_hull_polygon(cluster_points, buffer_miles=5.0)
            
            center_lat, center_lon = self._compute_cluster_centroid(primary_cluster)
            
            max_dist = max(
                self._distance_miles(center_lat, center_lon, float(s.latitude), float(s.longitude))
                for s in primary_cluster
            )
            radius_miles = max_dist + 5.0
            signal_count = len(primary_cluster)
            included_cities = list(set([str(s.city) for s in primary_cluster if s.city]))
        else:
            radius_miles = self._calculate_optimal_radius(nearby_signals, demographics)
            geojson_polygon = self._create_circle_polygon(center_lat, center_lon, radius_miles)
            signal_count = len([s for s in nearby_signals if self._distance_miles(
                center_lat, center_lon, float(s.latitude or 0), float(s.longitude or 0)
            ) <= radius_miles])
            included_cities = list(set([
                str(s.city) for s in nearby_signals 
                if s.city and self._distance_miles(
                    center_lat, center_lon, float(s.latitude or 0), float(s.longitude or 0)
                ) <= radius_miles
            ]))
        
        signal_density = signal_count / (math.pi * radius_miles ** 2) if radius_miles > 0 else 0
        
        total_population = None
        total_households = None
        median_income = None
        
        if demographics:
            total_population = demographics.get('population')
            total_households = demographics.get('total_households') or demographics.get('households')
            median_income = demographics.get('median_income')
        
        addressable_market = self._estimate_addressable_market(
            opportunity.category,
            total_population,
            median_income,
            signal_density
        )
        
        service_area = ServiceAreaBoundary(
            opportunity_id=opportunity.id,
            boundary_type="computed",
            center_latitude=center_lat,
            center_longitude=center_lon,
            radius_miles=radius_miles,
            geojson_polygon=geojson_polygon,
            included_cities=included_cities,
            total_population=total_population,
            total_households=total_households,
            median_income=median_income,
            signal_count=signal_count,
            signal_density=signal_density,
            addressable_market_value=addressable_market,
            computation_factors={
                "algorithm_version": "1.0",
                "nearby_signal_count": len(nearby_signals),
                "initial_radius": self.DEFAULT_RADIUS_MILES,
                "adjusted_radius": radius_miles,
                "has_demographics": demographics is not None
            },
            is_active=True,
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        
        self.db.add(service_area)
        self.db.commit()
        self.db.refresh(service_area)
        
        return service_area
    
    def _find_nearby_signals(
        self,
        category: str,
        center_lat: float,
        center_lon: float,
        radius_miles: float
    ) -> List[Opportunity]:
        """Find opportunity signals near the center point."""
        lat_range = radius_miles / 69.0
        lon_range = radius_miles / (69.0 * math.cos(math.radians(center_lat)))
        
        signals = self.db.query(Opportunity).filter(
            Opportunity.category == category,
            Opportunity.latitude.isnot(None),
            Opportunity.longitude.isnot(None),
            Opportunity.latitude.between(center_lat - lat_range, center_lat + lat_range),
            Opportunity.longitude.between(center_lon - lon_range, center_lon + lon_range)
        ).all()
        
        return [s for s in signals if self._distance_miles(
            center_lat, center_lon, s.latitude, s.longitude
        ) <= radius_miles]
    
    def _cluster_signals(
        self,
        signals: List[Opportunity],
        eps_miles: float = 10.0,
        min_samples: int = 2
    ) -> List[List[Opportunity]]:
        """
        DBSCAN-like clustering of opportunity signals.
        Groups signals within eps_miles of each other.
        """
        if not signals:
            return []
        
        n = len(signals)
        visited = [False] * n
        clusters = []
        
        for i in range(n):
            if visited[i]:
                continue
            
            neighbors = self._get_neighbors(signals, i, eps_miles)
            
            if len(neighbors) < min_samples:
                continue
            
            cluster = []
            self._expand_cluster(signals, visited, i, neighbors, cluster, eps_miles, min_samples)
            
            if cluster:
                clusters.append(cluster)
        
        return clusters
    
    def _get_neighbors(
        self,
        signals: List[Opportunity],
        idx: int,
        eps_miles: float
    ) -> List[int]:
        """Find all signals within eps_miles of the signal at idx."""
        neighbors = []
        sig = signals[idx]
        
        for j, other in enumerate(signals):
            if self._distance_miles(
                float(sig.latitude), float(sig.longitude),
                float(other.latitude), float(other.longitude)
            ) <= eps_miles:
                neighbors.append(j)
        
        return neighbors
    
    def _expand_cluster(
        self,
        signals: List[Opportunity],
        visited: List[bool],
        idx: int,
        neighbors: List[int],
        cluster: List[Opportunity],
        eps_miles: float,
        min_samples: int
    ) -> None:
        """Expand cluster from seed point using density reachability."""
        visited[idx] = True
        cluster.append(signals[idx])
        
        i = 0
        while i < len(neighbors):
            neighbor_idx = neighbors[i]
            
            if not visited[neighbor_idx]:
                visited[neighbor_idx] = True
                cluster.append(signals[neighbor_idx])
                
                new_neighbors = self._get_neighbors(signals, neighbor_idx, eps_miles)
                if len(new_neighbors) >= min_samples:
                    neighbors.extend([n for n in new_neighbors if n not in neighbors])
            
            i += 1
    
    def _compute_cluster_centroid(
        self,
        cluster: List[Opportunity]
    ) -> Tuple[float, float]:
        """Compute the centroid of a cluster of signals."""
        if not cluster:
            return (0.0, 0.0)
        
        lat_sum = sum(float(s.latitude) for s in cluster)
        lon_sum = sum(float(s.longitude) for s in cluster)
        n = len(cluster)
        
        return (lat_sum / n, lon_sum / n)
    
    def _create_convex_hull_polygon(
        self,
        points: List[Tuple[float, float]],
        buffer_miles: float = 5.0
    ) -> Dict[str, Any]:
        """Create a GeoJSON polygon from a convex hull of points with buffer."""
        if len(points) < 3:
            if len(points) == 0:
                return {"type": "Polygon", "coordinates": [[]]}
            center_lat = sum(p[0] for p in points) / len(points)
            center_lon = sum(p[1] for p in points) / len(points)
            return self._create_circle_polygon(center_lat, center_lon, buffer_miles)
        
        hull = self._graham_scan(points)
        
        buffered_hull = self._buffer_polygon(hull, buffer_miles)
        
        coordinates = [[lon, lat] for lat, lon in buffered_hull]
        if coordinates and coordinates[0] != coordinates[-1]:
            coordinates.append(coordinates[0])
        
        return {
            "type": "Polygon",
            "coordinates": [coordinates]
        }
    
    def _graham_scan(
        self,
        points: List[Tuple[float, float]]
    ) -> List[Tuple[float, float]]:
        """Compute convex hull using Graham scan algorithm."""
        def cross(O, A, B):
            return (A[0] - O[0]) * (B[1] - O[1]) - (A[1] - O[1]) * (B[0] - O[0])
        
        points = sorted(set(points))
        if len(points) <= 1:
            return points
        
        lower = []
        for p in points:
            while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
                lower.pop()
            lower.append(p)
        
        upper = []
        for p in reversed(points):
            while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
                upper.pop()
            upper.append(p)
        
        return lower[:-1] + upper[:-1]
    
    def _buffer_polygon(
        self,
        points: List[Tuple[float, float]],
        buffer_miles: float
    ) -> List[Tuple[float, float]]:
        """Add a buffer around polygon points."""
        if not points:
            return []
        
        center_lat = sum(p[0] for p in points) / len(points)
        center_lon = sum(p[1] for p in points) / len(points)
        
        buffered = []
        for lat, lon in points:
            direction_lat = lat - center_lat
            direction_lon = lon - center_lon
            
            dist = math.sqrt(direction_lat**2 + direction_lon**2)
            if dist > 0:
                buffer_lat = buffer_miles / 69.0
                buffer_lon = buffer_miles / (69.0 * math.cos(math.radians(lat)))
                
                new_lat = lat + (direction_lat / dist) * buffer_lat
                new_lon = lon + (direction_lon / dist) * buffer_lon
                buffered.append((new_lat, new_lon))
            else:
                buffered.append((lat, lon))
        
        return buffered
    
    def _calculate_optimal_radius(
        self,
        nearby_signals: List[Opportunity],
        demographics: Optional[Dict]
    ) -> float:
        """Calculate optimal service area radius based on signal density."""
        if len(nearby_signals) == 0:
            return self.DEFAULT_RADIUS_MILES
        
        base_radius = self.DEFAULT_RADIUS_MILES
        
        if len(nearby_signals) >= self.SIGNAL_DENSITY_THRESHOLDS["high"]:
            base_radius = self.MIN_RADIUS_MILES + 10
        elif len(nearby_signals) >= self.SIGNAL_DENSITY_THRESHOLDS["medium"]:
            base_radius = self.DEFAULT_RADIUS_MILES
        else:
            base_radius = self.DEFAULT_RADIUS_MILES + 15
        
        if demographics:
            population = demographics.get('population', 0)
            if population > 1_000_000:
                base_radius *= 0.7
            elif population > 500_000:
                base_radius *= 0.85
            elif population < 100_000:
                base_radius *= 1.3
        
        return max(self.MIN_RADIUS_MILES, min(self.MAX_RADIUS_MILES, base_radius))
    
    def _distance_miles(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """Calculate distance between two points in miles using Haversine formula."""
        R = 3959
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def _create_circle_polygon(
        self,
        center_lat: float,
        center_lon: float,
        radius_miles: float,
        num_points: int = 32
    ) -> Dict[str, Any]:
        """Create a GeoJSON polygon approximating a circle."""
        coordinates = []
        
        for i in range(num_points):
            angle = (2 * math.pi * i) / num_points
            
            delta_lat = (radius_miles / 69.0) * math.cos(angle)
            delta_lon = (radius_miles / (69.0 * math.cos(math.radians(center_lat)))) * math.sin(angle)
            
            point_lat = center_lat + delta_lat
            point_lon = center_lon + delta_lon
            
            coordinates.append([point_lon, point_lat])
        
        coordinates.append(coordinates[0])
        
        return {
            "type": "Polygon",
            "coordinates": [coordinates]
        }
    
    def _geocode_from_city(
        self,
        city: Optional[str],
        region: Optional[str]
    ) -> Tuple[Optional[float], Optional[float]]:
        """Get approximate coordinates for a city/region."""
        city_coords = {
            "Austin": (30.2672, -97.7431),
            "Houston": (29.7604, -95.3698),
            "Dallas": (32.7767, -96.7970),
            "San Antonio": (29.4241, -98.4936),
            "Phoenix": (33.4484, -112.0740),
            "Los Angeles": (34.0522, -118.2437),
            "San Francisco": (37.7749, -122.4194),
            "New York": (40.7128, -74.0060),
            "Chicago": (41.8781, -87.6298),
            "Miami": (25.7617, -80.1918),
            "Seattle": (47.6062, -122.3321),
            "Denver": (39.7392, -104.9903),
            "Atlanta": (33.7490, -84.3880),
            "Boston": (42.3601, -71.0589),
            "Portland": (45.5152, -122.6784),
        }
        
        if city and city in city_coords:
            return city_coords[city]
        
        return None, None
    
    def _estimate_addressable_market(
        self,
        category: str,
        population: Optional[int],
        median_income: Optional[int],
        signal_density: float
    ) -> Optional[float]:
        """Estimate addressable market value for the service area."""
        if not population:
            return None
        
        category_spend = {
            "Home Services": 3500,
            "Healthcare": 4200,
            "Transportation": 2800,
            "Food & Beverage": 2400,
            "Professional Services": 1800,
            "Technology": 1500,
            "Retail": 3200,
            "Education": 2100,
            "Entertainment": 1200,
            "Financial Services": 1600,
        }
        
        base_spend = category_spend.get(category, 2000)
        
        income_multiplier = 1.0
        if median_income:
            income_multiplier = min(1.5, max(0.7, median_income / 65000))
        
        density_multiplier = 1.0 + min(0.5, signal_density * 10)
        
        addressable_market = population * base_spend * 0.15 * income_multiplier * density_multiplier
        
        return round(addressable_market, 2)
    
    def compute_growth_trajectory(
        self,
        state_fips: str,
        county_fips: Optional[str],
        city: Optional[str],
        population_data: Dict[str, Any]
    ) -> MarketGrowthTrajectory:
        """Compute and store a market growth trajectory."""
        existing = self.db.query(MarketGrowthTrajectory).filter(
            MarketGrowthTrajectory.state_fips == state_fips,
            MarketGrowthTrajectory.county_fips == county_fips,
            MarketGrowthTrajectory.is_active == True
        ).first()
        
        if existing and existing.computed_at and existing.computed_at.replace(tzinfo=timezone.utc) > datetime.now(timezone.utc) - timedelta(days=30):
            return existing
        
        if existing:
            existing.is_active = False
            self.db.commit()
        
        pop_growth = population_data.get('yoy_growth_rate', 0) or 0
        job_growth = population_data.get('job_growth_rate', 0) or 0
        income_growth = population_data.get('income_growth_rate', 0) or 0
        net_migration = population_data.get('net_migration_rate', 0) or 0
        
        growth_score = self._calculate_growth_score(
            pop_growth, job_growth, income_growth, net_migration
        )
        
        if growth_score >= 80:
            category = GrowthCategory.BOOMING
        elif growth_score >= 60:
            category = GrowthCategory.GROWING
        elif growth_score >= 40:
            category = GrowthCategory.STABLE
        else:
            category = GrowthCategory.DECLINING
        
        trajectory = MarketGrowthTrajectory(
            state_fips=state_fips,
            county_fips=county_fips,
            city=city,
            geography_name=population_data.get('geography_name', 'Unknown'),
            latitude=population_data.get('latitude'),
            longitude=population_data.get('longitude'),
            growth_category=category,
            growth_score=growth_score,
            population_growth_rate=pop_growth,
            job_growth_rate=job_growth,
            income_growth_rate=income_growth,
            net_migration_rate=net_migration,
            migration_trend="inflow" if net_migration > 0 else "outflow" if net_migration < 0 else "neutral",
            trajectory_factors={
                "pop_weight": 0.3,
                "job_weight": 0.3,
                "income_weight": 0.2,
                "migration_weight": 0.2
            },
            data_year=datetime.utcnow().year,
            is_active=True,
            expires_at=datetime.utcnow() + timedelta(days=90)
        )
        
        self.db.add(trajectory)
        self.db.commit()
        self.db.refresh(trajectory)
        
        return trajectory
    
    def _calculate_growth_score(
        self,
        pop_growth: float,
        job_growth: float,
        income_growth: float,
        net_migration: float
    ) -> float:
        """Calculate composite growth score (0-100)."""
        pop_score = min(100, max(0, 50 + (pop_growth * 10)))
        job_score = min(100, max(0, 50 + (job_growth * 10)))
        income_score = min(100, max(0, 50 + (income_growth * 10)))
        migration_score = min(100, max(0, 50 + (net_migration * 5)))
        
        return (
            pop_score * 0.3 +
            job_score * 0.3 +
            income_score * 0.2 +
            migration_score * 0.2
        )
