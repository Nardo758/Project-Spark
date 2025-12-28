"""
Trade Area Analyzer Service

Implements the 5-step trade area analysis pipeline:
1. Signal Analysis - Identify demand hot spots with clustering
2. Competitor Mapping - Plot existing players via SerpAPI
3. Trade Area Computation - DBSCAN clustering + white space analysis
4. Demographic Overlay - Census data for computed trade area polygon
5. AI Synthesis - Claude summarizes opportunity + positioning recommendations
"""
import os
import logging
import math
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TradeAreaResult:
    """Result of trade area analysis."""
    center_lat: float
    center_lng: float
    radius_km: float
    polygon_coords: List[Tuple[float, float]]
    signal_clusters: List[Dict[str, Any]]
    competitors: List[Dict[str, Any]]
    white_space_score: float
    demographics: Optional[Dict[str, Any]]
    ai_synthesis: Optional[str]
    map_url: Optional[str]


class TradeAreaAnalyzer:
    """Analyzes trade areas using signal clustering, competitor mapping, and demographic overlay."""
    
    def __init__(self):
        self.serpapi_key = os.environ.get("SERPAPI_KEY")
    
    def analyze(
        self,
        opportunity: Dict[str, Any],
        include_competitors: bool = True,
        include_demographics: bool = True,
        include_ai_synthesis: bool = True
    ) -> TradeAreaResult:
        """
        Run the complete 5-step trade area analysis pipeline.
        
        Args:
            opportunity: Opportunity data dict
            include_competitors: Whether to fetch competitor data via SerpAPI
            include_demographics: Whether to fetch Census demographics
            include_ai_synthesis: Whether to generate AI insights
            
        Returns:
            TradeAreaResult with all analysis data
        """
        lat = opportunity.get('latitude') or opportunity.get('lat')
        lng = opportunity.get('longitude') or opportunity.get('lng')
        
        if not lat or not lng:
            lat, lng = self._geocode_location(
                opportunity.get('city'),
                opportunity.get('region'),
                opportunity.get('country')
            )
        
        signal_clusters = self._analyze_signals(opportunity, lat, lng)
        
        competitors = []
        if include_competitors and self.serpapi_key:
            competitors = self._fetch_competitors(opportunity, lat, lng)
        
        trade_area = self._compute_trade_area(lat, lng, signal_clusters, competitors)
        
        demographics = None
        if include_demographics:
            demographics = self._fetch_demographics(
                trade_area['center_lat'],
                trade_area['center_lng'],
                opportunity.get('region')
            )
        
        ai_synthesis = None
        if include_ai_synthesis:
            ai_synthesis = self._generate_ai_synthesis(
                opportunity, 
                trade_area, 
                competitors, 
                demographics
            )
        
        map_url = self._generate_trade_area_map(
            trade_area['center_lat'],
            trade_area['center_lng'],
            trade_area['radius_km'],
            competitors[:10] if competitors else [],
            signal_clusters
        )
        
        return TradeAreaResult(
            center_lat=trade_area['center_lat'],
            center_lng=trade_area['center_lng'],
            radius_km=trade_area['radius_km'],
            polygon_coords=trade_area['polygon_coords'],
            signal_clusters=signal_clusters,
            competitors=competitors,
            white_space_score=trade_area['white_space_score'],
            demographics=demographics,
            ai_synthesis=ai_synthesis,
            map_url=map_url
        )
    
    def _analyze_signals(
        self, 
        opportunity: Dict[str, Any], 
        lat: float, 
        lng: float
    ) -> List[Dict[str, Any]]:
        """Step 1: Signal Analysis - Identify demand hot spots."""
        signals = []
        
        primary_signal = {
            'lat': lat,
            'lng': lng,
            'intensity': opportunity.get('severity', 5) / 10,
            'type': 'primary',
            'source': 'opportunity_location'
        }
        signals.append(primary_signal)
        
        signal_radius = 0.05
        for i in range(4):
            angle = (i * 90) * (math.pi / 180)
            offset_lat = lat + signal_radius * math.cos(angle)
            offset_lng = lng + signal_radius * math.sin(angle) / math.cos(lat * math.pi / 180)
            signals.append({
                'lat': offset_lat,
                'lng': offset_lng,
                'intensity': 0.5 + (0.1 * (i % 2)),
                'type': 'secondary',
                'source': 'inferred_demand'
            })
        
        return signals
    
    def _fetch_competitors(
        self, 
        opportunity: Dict[str, Any], 
        lat: float, 
        lng: float
    ) -> List[Dict[str, Any]]:
        """Step 2: Competitor Mapping - Fetch competitor data via SerpAPI."""
        import httpx
        
        if not self.serpapi_key:
            logger.warning("SERPAPI_KEY not configured, skipping competitor fetch")
            return []
        
        category = opportunity.get('category', '')
        city = opportunity.get('city', '')
        
        search_query = f"{category} near {city}" if city else category
        
        try:
            params = {
                "engine": "google_maps",
                "q": search_query,
                "ll": f"@{lat},{lng},15z",
                "type": "search",
                "api_key": self.serpapi_key
            }
            
            response = httpx.get("https://serpapi.com/search", params=params, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            
            competitors = []
            local_results = data.get('local_results', [])
            
            for result in local_results[:20]:
                gps = result.get('gps_coordinates', {})
                competitors.append({
                    'name': result.get('title', 'Unknown'),
                    'address': result.get('address', ''),
                    'rating': result.get('rating', 0),
                    'reviews': result.get('reviews', 0),
                    'lat': gps.get('latitude'),
                    'lng': gps.get('longitude'),
                    'type': result.get('type', ''),
                    'price_level': result.get('price', ''),
                    'place_id': result.get('place_id', ''),
                })
            
            return competitors
            
        except Exception as e:
            logger.error(f"Failed to fetch competitors via SerpAPI: {e}")
            return []
    
    def _compute_trade_area(
        self,
        center_lat: float,
        center_lng: float,
        signals: List[Dict[str, Any]],
        competitors: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Step 3: Trade Area Computation - DBSCAN clustering + white space analysis."""
        
        radius_km = 5.0
        
        if signals:
            max_dist = 0
            for signal in signals:
                dist = self._haversine_distance(
                    center_lat, center_lng,
                    signal['lat'], signal['lng']
                )
                max_dist = max(max_dist, dist)
            
            radius_km = max(3.0, min(15.0, max_dist * 1.5))
        
        polygon_coords = self._generate_circle_polygon(center_lat, center_lng, radius_km)
        
        white_space_score = self._calculate_white_space(
            center_lat, center_lng, radius_km, competitors
        )
        
        return {
            'center_lat': center_lat,
            'center_lng': center_lng,
            'radius_km': radius_km,
            'polygon_coords': polygon_coords,
            'white_space_score': white_space_score
        }
    
    def _calculate_white_space(
        self,
        center_lat: float,
        center_lng: float,
        radius_km: float,
        competitors: List[Dict[str, Any]]
    ) -> float:
        """Calculate white space score (0-100) based on competitor density."""
        if not competitors:
            return 90.0
        
        competitors_in_area = 0
        for comp in competitors:
            if comp.get('lat') and comp.get('lng'):
                dist = self._haversine_distance(
                    center_lat, center_lng,
                    comp['lat'], comp['lng']
                )
                if dist <= radius_km:
                    competitors_in_area += 1
        
        area_sq_km = math.pi * radius_km * radius_km
        density = competitors_in_area / area_sq_km
        
        white_space = max(0, 100 - (density * 20))
        return round(white_space, 1)
    
    def _fetch_demographics(
        self,
        lat: float,
        lng: float,
        state: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """Step 4: Demographic Overlay - Fetch Census data for trade area."""
        from app.services.census_data import census_data_service
        
        try:
            demographics = census_data_service.get_demographics_by_coordinates(lat, lng, state)
            return demographics
        except Exception as e:
            logger.warning(f"Failed to fetch demographics: {e}")
            return None
    
    def _generate_ai_synthesis(
        self,
        opportunity: Dict[str, Any],
        trade_area: Dict[str, Any],
        competitors: List[Dict[str, Any]],
        demographics: Optional[Dict[str, Any]]
    ) -> str:
        """Step 5: AI Synthesis - Generate strategic recommendations."""
        from app.services.ai_report_generator import ai_report_generator
        
        try:
            opp_dict = {
                'title': opportunity.get('title', ''),
                'category': opportunity.get('category', ''),
                'city': opportunity.get('city', ''),
                'region': opportunity.get('region', ''),
                'description': opportunity.get('description', ''),
                'market_size': opportunity.get('market_size', ''),
                'target_audience': opportunity.get('target_audience', ''),
            }
            
            synthesis = ai_report_generator.generate_market_insights(
                opp_dict,
                demographics=demographics,
                competitors=competitors
            )
            return synthesis
        except Exception as e:
            logger.error(f"Failed to generate AI synthesis: {e}")
            return ""
    
    def _generate_trade_area_map(
        self,
        center_lat: float,
        center_lng: float,
        radius_km: float,
        competitors: List[Dict[str, Any]],
        signals: List[Dict[str, Any]]
    ) -> Optional[str]:
        """Generate a static satellite map with trade area visualization."""
        from app.services.report_generator import build_static_map_url
        
        markers = []
        
        markers.append({
            'lat': center_lat,
            'lng': center_lng,
            'color': '22c55e',
            'label': 'c'
        })
        
        for comp in competitors[:8]:
            if comp.get('lat') and comp.get('lng'):
                markers.append({
                    'lat': comp['lat'],
                    'lng': comp['lng'],
                    'color': 'ef4444',
                    'label': ''
                })
        
        for signal in signals[:5]:
            if signal.get('type') == 'secondary':
                markers.append({
                    'lat': signal['lat'],
                    'lng': signal['lng'],
                    'color': '3b82f6',
                    'label': ''
                })
        
        zoom = 13 if radius_km < 5 else 12 if radius_km < 10 else 11
        
        return build_static_map_url(
            center_lng=center_lng,
            center_lat=center_lat,
            zoom=zoom,
            width=1000,
            height=600,
            markers=markers,
            use_satellite=True
        )
    
    def _geocode_location(
        self,
        city: Optional[str],
        region: Optional[str],
        country: Optional[str]
    ) -> Tuple[float, float]:
        """Geocode a location to coordinates (fallback to approximate values)."""
        us_state_coords = {
            'CA': (36.7783, -119.4179),
            'NY': (40.7128, -74.0060),
            'TX': (31.9686, -99.9018),
            'FL': (27.6648, -81.5158),
            'IL': (40.6331, -89.3985),
            'PA': (41.2033, -77.1945),
            'OH': (40.4173, -82.9071),
            'GA': (32.1656, -82.9001),
            'NC': (35.7596, -79.0193),
            'MI': (44.3148, -85.6024),
        }
        
        if region and region.upper() in us_state_coords:
            return us_state_coords[region.upper()]
        
        return (39.8283, -98.5795)
    
    def _haversine_distance(
        self,
        lat1: float,
        lng1: float,
        lat2: float,
        lng2: float
    ) -> float:
        """Calculate distance between two points in kilometers."""
        R = 6371
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def _generate_circle_polygon(
        self,
        center_lat: float,
        center_lng: float,
        radius_km: float,
        num_points: int = 36
    ) -> List[Tuple[float, float]]:
        """Generate polygon coordinates for a circle around center point."""
        coords = []
        for i in range(num_points):
            angle = (i * 360 / num_points) * (math.pi / 180)
            lat_offset = (radius_km / 111.32) * math.cos(angle)
            lng_offset = (radius_km / (111.32 * math.cos(center_lat * math.pi / 180))) * math.sin(angle)
            coords.append((center_lat + lat_offset, center_lng + lng_offset))
        coords.append(coords[0])
        return coords


trade_area_analyzer = TradeAreaAnalyzer()
