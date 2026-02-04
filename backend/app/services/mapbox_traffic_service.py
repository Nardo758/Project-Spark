"""
Mapbox Traffic Service

Fetches real-time traffic congestion data from Mapbox Traffic v1 tileset.
Provides live congestion levels that can be compared against DOT AADT baseline
to identify leading indicators of traffic growth or decline.

Mapbox Traffic API:
- Tilequery: https://api.mapbox.com/v4/mapbox.mapbox-traffic-v1/tilequery/{lng},{lat}.json
- Updates every ~8 minutes
- Congestion levels: low, moderate, heavy, severe
"""

import os
import logging
import requests
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class CongestionLevel(Enum):
    """Mapbox congestion levels with numeric values for comparison."""
    LOW = 1
    MODERATE = 2
    HEAVY = 3
    SEVERE = 4
    UNKNOWN = 0
    
    @classmethod
    def from_string(cls, value: str) -> 'CongestionLevel':
        mapping = {
            'low': cls.LOW,
            'moderate': cls.MODERATE,
            'heavy': cls.HEAVY,
            'severe': cls.SEVERE
        }
        return mapping.get(value.lower(), cls.UNKNOWN) if value else cls.UNKNOWN


@dataclass
class LiveTrafficResult:
    """Result from Mapbox live traffic query."""
    congestion: CongestionLevel
    congestion_label: str
    road_class: Optional[str] = None
    source: str = 'mapbox_live'
    raw_data: Optional[Dict] = None


@dataclass 
class TrafficComparisonResult:
    """Comparison between live Mapbox traffic and DOT AADT baseline."""
    live_congestion: CongestionLevel
    expected_congestion: CongestionLevel
    delta: int  # Positive = more congested than expected, negative = less
    signal: str  # 'growth', 'decline', 'stable'
    signal_strength: str  # 'strong', 'moderate', 'weak'
    description: str


# Expected congestion based on AADT thresholds
AADT_CONGESTION_THRESHOLDS = {
    'low': (0, 10000),       # 0-10K AADT = expect low congestion
    'moderate': (10000, 35000),  # 10K-35K = expect moderate
    'heavy': (35000, 75000),     # 35K-75K = expect heavy
    'severe': (75000, float('inf'))  # 75K+ = expect severe
}


class MapboxTrafficService:
    """Service to fetch real-time traffic data from Mapbox."""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.access_token = os.environ.get('MAPBOX_ACCESS_TOKEN')
        self.base_url = "https://api.mapbox.com/v4/mapbox.mapbox-traffic-v1/tilequery"
    
    def _get_live_traffic_at_point(
        self,
        lat: float,
        lng: float,
        radius: int = 50  # meters
    ) -> Optional[LiveTrafficResult]:
        """
        Query Mapbox tilequery API for live traffic at a specific point.
        
        Args:
            lat: Latitude
            lng: Longitude
            radius: Search radius in meters (default 50m)
            
        Returns:
            LiveTrafficResult or None if no data available
        """
        if not self.access_token:
            logger.warning("MAPBOX_ACCESS_TOKEN not set, cannot fetch live traffic")
            return None
        
        try:
            url = f"{self.base_url}/{lng},{lat}.json"
            params = {
                'access_token': self.access_token,
                'radius': radius,
                'limit': 5,
                'layers': 'traffic'
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            features = data.get('features', [])
            if not features:
                return None
            
            # Get the closest/most relevant feature
            feature = features[0]
            props = feature.get('properties', {})
            
            congestion_str = props.get('congestion', '')
            congestion = CongestionLevel.from_string(congestion_str)
            
            return LiveTrafficResult(
                congestion=congestion,
                congestion_label=congestion_str or 'unknown',
                road_class=props.get('class'),
                source='mapbox_live',
                raw_data=props
            )
            
        except requests.RequestException as e:
            logger.error(f"Mapbox traffic API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching Mapbox traffic: {e}")
            return None
    
    def get_expected_congestion_from_aadt(self, aadt: int) -> CongestionLevel:
        """
        Determine expected congestion level based on DOT AADT baseline.
        
        Args:
            aadt: Annual Average Daily Traffic count
            
        Returns:
            Expected CongestionLevel
        """
        if aadt < AADT_CONGESTION_THRESHOLDS['low'][1]:
            return CongestionLevel.LOW
        elif aadt < AADT_CONGESTION_THRESHOLDS['moderate'][1]:
            return CongestionLevel.MODERATE
        elif aadt < AADT_CONGESTION_THRESHOLDS['heavy'][1]:
            return CongestionLevel.HEAVY
        else:
            return CongestionLevel.SEVERE
    
    def compare_live_vs_baseline(
        self,
        lat: float,
        lng: float,
        aadt: int
    ) -> Optional[TrafficComparisonResult]:
        """
        Compare live Mapbox traffic against DOT AADT baseline.
        
        This is the core "leading indicator" calculation.
        - If live congestion > expected: area may be growing
        - If live congestion < expected: area may be declining
        
        Args:
            lat: Latitude
            lng: Longitude
            aadt: DOT AADT baseline for this road segment
            
        Returns:
            TrafficComparisonResult with signal analysis
        """
        live_result = self._get_live_traffic_at_point(lat, lng)
        if not live_result or live_result.congestion == CongestionLevel.UNKNOWN:
            return None
        
        expected = self.get_expected_congestion_from_aadt(aadt)
        live = live_result.congestion
        
        delta = live.value - expected.value
        
        # Determine signal
        if delta >= 2:
            signal = 'growth'
            signal_strength = 'strong'
            description = f"Live traffic ({live.name.lower()}) significantly exceeds baseline ({expected.name.lower()}) - strong growth signal"
        elif delta == 1:
            signal = 'growth'
            signal_strength = 'moderate'
            description = f"Live traffic ({live.name.lower()}) exceeds baseline ({expected.name.lower()}) - moderate growth signal"
        elif delta <= -2:
            signal = 'decline'
            signal_strength = 'strong'
            description = f"Live traffic ({live.name.lower()}) significantly below baseline ({expected.name.lower()}) - strong decline signal"
        elif delta == -1:
            signal = 'decline'
            signal_strength = 'moderate'
            description = f"Live traffic ({live.name.lower()}) below baseline ({expected.name.lower()}) - moderate decline signal"
        else:
            signal = 'stable'
            signal_strength = 'weak'
            description = f"Live traffic ({live.name.lower()}) matches baseline ({expected.name.lower()}) - stable"
        
        return TrafficComparisonResult(
            live_congestion=live,
            expected_congestion=expected,
            delta=delta,
            signal=signal,
            signal_strength=signal_strength,
            description=description
        )
    
    def get_live_traffic_for_segments(
        self,
        segments: List[Dict[str, Any]],
        sample_rate: float = 0.2
    ) -> List[Dict[str, Any]]:
        """
        Get live traffic data for a list of road segments.
        
        To avoid excessive API calls, samples a subset of segments
        and extrapolates to nearby segments. Uses parallel requests
        for faster processing.
        
        Args:
            segments: List of road segments with lat/lng coordinates
            sample_rate: Fraction of segments to sample (0.0-1.0)
            
        Returns:
            Segments enriched with live traffic and leading indicator data
        """
        import random
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        if not segments:
            return segments
        
        # Sample segments for live traffic queries
        sample_size = max(1, int(len(segments) * sample_rate))
        sample_indices = set(random.sample(range(len(segments)), min(sample_size, len(segments))))
        
        # Prepare sampled segments for parallel processing
        segments_to_query = []
        for i in sample_indices:
            segment = segments[i]
            props = segment.get('properties', {})
            geometry = segment.get('geometry', {})
            coords = geometry.get('coordinates', [])
            if not coords:
                continue
            if isinstance(coords[0], list):
                mid_idx = len(coords) // 2
                lng, lat = coords[mid_idx][0], coords[mid_idx][1]
            else:
                lng, lat = coords[0], coords[1]
            aadt = props.get('aadt', 0)
            if aadt > 0:
                segments_to_query.append((i, lat, lng, aadt))
        
        # Parallel API calls for sampled segments
        sampled_results = {}
        def query_segment(args):
            idx, lat, lng, aadt = args
            grid_key = f"{round(lat, 2)},{round(lng, 2)}"
            comparison = self.compare_live_vs_baseline(lat, lng, aadt)
            return idx, grid_key, comparison
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(query_segment, args): args for args in segments_to_query}
            for future in as_completed(futures):
                try:
                    idx, grid_key, comparison = future.result()
                    if comparison:
                        sampled_results[idx] = comparison
                        sampled_results[grid_key] = comparison
                except Exception as e:
                    logger.warning(f"Mapbox query failed: {e}")
        
        # Enrich all segments with results
        enriched_segments = []
        for i, segment in enumerate(segments):
            enriched = segment.copy()
            props = enriched.get('properties', {})
            
            geometry = segment.get('geometry', {})
            coords = geometry.get('coordinates', [])
            if coords:
                if isinstance(coords[0], list):
                    mid_idx = len(coords) // 2
                    lng, lat = coords[mid_idx][0], coords[mid_idx][1]
                else:
                    lng, lat = coords[0], coords[1]
                
                grid_key = f"{round(lat, 2)},{round(lng, 2)}"
                comparison = sampled_results.get(i) or sampled_results.get(grid_key)
                
                if comparison:
                    props['live_congestion'] = comparison.live_congestion.name.lower()
                    props['expected_congestion'] = comparison.expected_congestion.name.lower()
                    props['traffic_signal'] = comparison.signal
                    props['signal_strength'] = comparison.signal_strength
                    props['signal_delta'] = comparison.delta
                    props['signal_description'] = comparison.description
            
            enriched['properties'] = props
            enriched_segments.append(enriched)
        
        return enriched_segments
    
    def get_congestion_color(self, congestion: str) -> str:
        """Get color for congestion level visualization."""
        colors = {
            'low': '#22c55e',      # Green
            'moderate': '#eab308', # Yellow
            'heavy': '#f97316',    # Orange
            'severe': '#ef4444'    # Red
        }
        return colors.get(congestion.lower(), '#6b7280')  # Gray default
    
    def get_signal_color(self, signal: str) -> str:
        """Get color for leading indicator signal."""
        colors = {
            'growth': '#22c55e',   # Green - growing
            'stable': '#3b82f6',   # Blue - stable
            'decline': '#ef4444'   # Red - declining
        }
        return colors.get(signal.lower(), '#6b7280')
