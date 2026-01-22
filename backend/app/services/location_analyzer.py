"""
Location Analyzer Service

Shared analysis engine that identifies optimal business locations within a target area.
Used by Deep Clone, Competition, and Demographics layers to find best sub-zones.

Features:
- Grid sampling across target radius
- Scoring functions based on demographics, competition density, market signals
- Weighted scoring based on active layer configurations
- Returns ranked optimal zones with explanations
"""

import math
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class GridPoint:
    lat: float
    lng: float
    

@dataclass
class ScoredZone:
    id: str
    center_lat: float
    center_lng: float
    radius_miles: float
    total_score: float
    scores: Dict[str, float]
    insights: List[str]
    rank: int = 0


@dataclass
class ScoringWeights:
    demographics: float = 0.4
    competition: float = 0.4
    market_signals: float = 0.2


class LocationAnalyzer:
    DEFAULT_ANALYSIS_RADIUS = 3.0
    MIN_GRID_POINTS = 7
    MAX_GRID_POINTS = 19
    
    @staticmethod
    def generate_grid_points(
        center_lat: float,
        center_lng: float,
        radius_miles: float,
        num_rings: int = 2
    ) -> List[GridPoint]:
        """
        Generate a grid of candidate center points within the target radius.
        Uses hexagonal-style pattern for even coverage.
        """
        points = [GridPoint(lat=center_lat, lng=center_lng)]
        
        miles_per_degree_lat = 69.0
        miles_per_degree_lng = 69.0 * math.cos(math.radians(center_lat))
        
        for ring in range(1, num_rings + 1):
            ring_radius = (radius_miles * ring) / (num_rings + 1)
            num_points_in_ring = 6 * ring
            
            for i in range(num_points_in_ring):
                angle = (2 * math.pi * i) / num_points_in_ring
                
                delta_miles_lat = ring_radius * math.cos(angle)
                delta_miles_lng = ring_radius * math.sin(angle)
                
                delta_lat = delta_miles_lat / miles_per_degree_lat
                delta_lng = delta_miles_lng / miles_per_degree_lng
                
                points.append(GridPoint(
                    lat=center_lat + delta_lat,
                    lng=center_lng + delta_lng
                ))
        
        return points
    
    @staticmethod
    def score_demographics(
        demographics_data: Optional[Dict[str, Any]],
        business_type: Optional[str] = None
    ) -> Tuple[float, List[str]]:
        """
        Score a location based on demographics data.
        Returns (score 0-100, list of insights)
        """
        if not demographics_data:
            return 50.0, ["No demographics data available"]
        
        score = 50.0
        insights = []
        
        population = demographics_data.get("total_population", 0)
        if population:
            if population > 100000:
                score += 15
                insights.append(f"High population density ({population:,} residents)")
            elif population > 50000:
                score += 10
                insights.append(f"Good population base ({population:,} residents)")
            elif population > 20000:
                score += 5
        
        income = demographics_data.get("median_income", 0)
        if income:
            if income > 80000:
                score += 15
                insights.append(f"High income area (${income:,} median)")
            elif income > 60000:
                score += 10
                insights.append(f"Above average income (${income:,} median)")
            elif income > 40000:
                score += 5
        
        households = demographics_data.get("total_households", 0)
        if households and households > 30000:
            score += 5
            insights.append(f"Strong household count ({households:,})")
        
        return min(100.0, max(0.0, score)), insights
    
    @staticmethod
    def score_competition(
        competitors: List[Dict[str, Any]],
        ideal_competitor_count: int = 3
    ) -> Tuple[float, List[str]]:
        """
        Score based on competition density.
        Too few = no proven market, too many = saturated.
        """
        if competitors is None:
            return 50.0, ["No competition data available"]
        
        count = len(competitors)
        insights = []
        
        if count == 0:
            score = 40.0
            insights.append("No direct competitors found - unproven market")
        elif count <= ideal_competitor_count:
            score = 90.0 - (count * 5)
            insights.append(f"Low competition ({count} competitors) - market opportunity")
        elif count <= ideal_competitor_count * 2:
            score = 70.0 - ((count - ideal_competitor_count) * 5)
            insights.append(f"Moderate competition ({count} competitors)")
        else:
            score = 40.0 - min(20, (count - ideal_competitor_count * 2) * 2)
            insights.append(f"High competition ({count} competitors) - saturated market")
        
        if competitors:
            avg_rating = sum(c.get("rating", 0) for c in competitors) / len(competitors)
            if avg_rating < 3.5:
                score += 10
                insights.append(f"Competitors have low ratings ({avg_rating:.1f}/5) - quality gap opportunity")
            elif avg_rating > 4.5:
                score -= 5
                insights.append(f"Strong competitors with high ratings ({avg_rating:.1f}/5)")
        
        return min(100.0, max(0.0, score)), insights
    
    @staticmethod
    def score_market_signals(
        deep_clone_data: Optional[Dict[str, Any]] = None
    ) -> Tuple[float, List[str]]:
        """
        Score based on market signals from Deep Clone analysis.
        """
        if not deep_clone_data:
            return 50.0, ["No market signal data available"]
        
        score = 50.0
        insights = []
        
        if deep_clone_data.get("market_gap_identified"):
            score += 20
            insights.append("Market gap identified in area")
        
        if deep_clone_data.get("growth_trend"):
            trend = deep_clone_data["growth_trend"]
            if trend == "high":
                score += 15
                insights.append("High growth trend detected")
            elif trend == "moderate":
                score += 8
                insights.append("Moderate growth potential")
        
        if deep_clone_data.get("demand_signals"):
            score += 10
            insights.append("Strong demand signals present")
        
        return min(100.0, max(0.0, score)), insights
    
    def analyze_zone(
        self,
        point: GridPoint,
        radius_miles: float,
        demographics_data: Optional[Dict[str, Any]] = None,
        competitors: Optional[List[Dict[str, Any]]] = None,
        deep_clone_data: Optional[Dict[str, Any]] = None,
        weights: Optional[ScoringWeights] = None,
        business_type: Optional[str] = None
    ) -> ScoredZone:
        """
        Analyze a single candidate zone and return scored result.
        """
        if weights is None:
            weights = ScoringWeights()
        
        demo_score, demo_insights = self.score_demographics(demographics_data, business_type)
        comp_score, comp_insights = self.score_competition(competitors or [])
        market_score, market_insights = self.score_market_signals(deep_clone_data)
        
        total_score = (
            demo_score * weights.demographics +
            comp_score * weights.competition +
            market_score * weights.market_signals
        )
        
        all_insights = demo_insights + comp_insights + market_insights
        
        zone_id = f"zone_{point.lat:.4f}_{point.lng:.4f}"
        
        return ScoredZone(
            id=zone_id,
            center_lat=point.lat,
            center_lng=point.lng,
            radius_miles=radius_miles,
            total_score=round(total_score, 1),
            scores={
                "demographics": round(demo_score, 1),
                "competition": round(comp_score, 1),
                "market_signals": round(market_score, 1)
            },
            insights=all_insights[:5]
        )
    
    def find_optimal_zones(
        self,
        center_lat: float,
        center_lng: float,
        target_radius_miles: float,
        analysis_radius_miles: float = 3.0,
        demographics_data: Optional[Dict[str, Any]] = None,
        competitors: Optional[List[Dict[str, Any]]] = None,
        deep_clone_data: Optional[Dict[str, Any]] = None,
        weights: Optional[ScoringWeights] = None,
        top_n: int = 3,
        business_type: Optional[str] = None
    ) -> List[ScoredZone]:
        """
        Find the top N optimal zones within the target radius.
        
        Args:
            center_lat, center_lng: Center of target area
            target_radius_miles: Size of the search area
            analysis_radius_miles: Size of each optimal zone (default 3 miles)
            demographics_data: Census data for scoring
            competitors: List of competitor businesses
            deep_clone_data: Market signal data
            weights: Scoring weight configuration
            top_n: Number of best zones to return
            business_type: Type of business for context-aware scoring
            
        Returns:
            List of top N ScoredZone objects, ranked by score
        """
        num_rings = 2 if target_radius_miles <= 10 else 3
        grid_points = self.generate_grid_points(
            center_lat, center_lng, target_radius_miles, num_rings
        )
        
        logger.info(f"Analyzing {len(grid_points)} candidate zones within {target_radius_miles}mi radius")
        
        scored_zones = []
        for point in grid_points:
            point_competitors = self._filter_competitors_for_point(
                competitors or [], point, analysis_radius_miles
            )
            
            zone = self.analyze_zone(
                point=point,
                radius_miles=analysis_radius_miles,
                demographics_data=demographics_data,
                competitors=point_competitors,
                deep_clone_data=deep_clone_data,
                weights=weights,
                business_type=business_type
            )
            scored_zones.append(zone)
        
        scored_zones.sort(key=lambda z: z.total_score, reverse=True)
        
        for i, zone in enumerate(scored_zones[:top_n]):
            zone.rank = i + 1
        
        return scored_zones[:top_n]
    
    def _filter_competitors_for_point(
        self,
        all_competitors: List[Dict[str, Any]],
        point: GridPoint,
        radius_miles: float
    ) -> List[Dict[str, Any]]:
        """
        Filter competitors that fall within the analysis radius of a point.
        """
        nearby = []
        for comp in all_competitors:
            comp_lat = comp.get("latitude") or comp.get("lat")
            comp_lng = comp.get("longitude") or comp.get("lng")
            
            if comp_lat is None or comp_lng is None:
                continue
            
            distance = self._haversine_distance(
                point.lat, point.lng, comp_lat, comp_lng
            )
            
            if distance <= radius_miles:
                nearby.append(comp)
        
        return nearby
    
    @staticmethod
    def _haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """
        Calculate distance in miles between two coordinates.
        """
        R = 3959
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c


def get_layer_weights(active_layers: List[str]) -> ScoringWeights:
    """
    Get scoring weights based on which layers are active.
    """
    weights = ScoringWeights(demographics=0.0, competition=0.0, market_signals=0.0)
    
    layer_count = len(active_layers)
    if layer_count == 0:
        return ScoringWeights()
    
    weight_per_layer = 1.0 / layer_count
    
    for layer in active_layers:
        if layer == "demographics":
            weights.demographics = weight_per_layer
        elif layer == "competition":
            weights.competition = weight_per_layer
        elif layer == "deep_clone":
            weights.demographics = weight_per_layer * 0.3
            weights.competition = weight_per_layer * 0.4
            weights.market_signals = weight_per_layer * 0.3
    
    return weights
