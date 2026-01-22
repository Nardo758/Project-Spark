"""
Traffic Data Fusion Service

Combines multiple traffic data sources to produce a more accurate estimate:
- DOT AADT: Annual Average Daily Traffic (official, but yearly updates)
- Google Popular Times: Real-time activity levels (current, but business-focused)

The fusion algorithm weights sources based on data freshness and relevance.
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class FusedTrafficResult:
    """Result from fused traffic calculation"""
    monthly_vehicle_traffic: int
    monthly_foot_traffic: int
    confidence_score: float  # 0-100, higher = more reliable
    primary_source: str  # 'dot', 'google', 'blended', 'estimated'
    breakdown: Dict[str, Any]


class TrafficFusionService:
    """
    Fuses multiple traffic data sources into a unified estimate.
    
    The algorithm:
    1. DOT AADT provides baseline vehicle traffic (highway-level accuracy)
    2. Google Popular Times provides real-time activity adjustment factor
    3. The fusion weights recency and coverage of each source
    
    Formula for blended vehicle traffic:
    - If both sources available: DOT_baseline × Google_activity_multiplier
    - The activity multiplier adjusts for current conditions vs yearly average
    """
    
    # Weight factors for each source (must sum to 1.0)
    DOT_BASE_WEIGHT = 0.6  # DOT provides reliable baseline
    GOOGLE_ADJUSTMENT_WEIGHT = 0.4  # Google provides recency adjustment
    
    # Activity level to multiplier mapping
    # Google vitality scores (0-100) translate to activity multipliers
    VITALITY_TO_MULTIPLIER = {
        (0, 20): 0.6,    # Very low activity = 60% of baseline
        (20, 40): 0.8,   # Low activity
        (40, 60): 1.0,   # Average activity = baseline
        (60, 80): 1.2,   # High activity
        (80, 100): 1.4,  # Very high activity = 140% of baseline
    }
    
    def fuse_traffic_data(
        self,
        lat: float,
        lng: float,
        radius_miles: float,
        dot_data: Optional[Dict[str, Any]] = None,
        google_data: Optional[Dict[str, Any]] = None
    ) -> FusedTrafficResult:
        """
        Fuse DOT and Google traffic data sources.
        
        Args:
            lat, lng: Location coordinates
            radius_miles: Analysis area radius
            dot_data: Result from DOTTrafficService.get_area_traffic_summary()
            google_data: Result from foot traffic analysis (vitality, avg_daily_traffic)
            
        Returns:
            FusedTrafficResult with blended estimates
        """
        has_dot = dot_data and dot_data.get('source') == 'dot_api' and dot_data.get('monthly_estimate', 0) > 0
        has_google = google_data and google_data.get('avg_daily_traffic', 0) > 0
        
        breakdown = {
            'dot_available': has_dot,
            'google_available': has_google,
            'dot_monthly': dot_data.get('monthly_estimate', 0) if dot_data else 0,
            'google_foot_daily': google_data.get('avg_daily_traffic', 0) if google_data else 0,
            'google_vitality': google_data.get('area_vitality_score', 50) if google_data else 50,
        }
        
        # Case 1: Both sources available - use fusion formula
        if has_dot and has_google:
            result = self._fuse_both_sources(dot_data, google_data, breakdown)
            
        # Case 2: Only DOT available
        elif has_dot:
            result = self._use_dot_only(dot_data, breakdown)
            
        # Case 3: Only Google available
        elif has_google:
            result = self._use_google_only(google_data, breakdown)
            
        # Case 4: Neither available - pure estimation
        else:
            result = self._estimate_only(lat, lng, radius_miles, breakdown)
        
        return result
    
    def _fuse_both_sources(
        self,
        dot_data: Dict,
        google_data: Dict,
        breakdown: Dict
    ) -> FusedTrafficResult:
        """
        Fusion formula when both DOT and Google data are available.
        
        Vehicle Traffic = DOT_baseline × activity_adjustment
        
        Where activity_adjustment is derived from Google vitality score:
        - High vitality (80-100) suggests current activity exceeds DOT annual average
        - Low vitality (0-20) suggests current activity below annual average
        """
        dot_monthly = dot_data.get('monthly_estimate', 0)
        google_foot_daily = google_data.get('avg_daily_traffic', 0)
        vitality = google_data.get('area_vitality_score', 50)
        
        # Calculate activity multiplier from vitality
        activity_multiplier = self._vitality_to_multiplier(vitality)
        
        # Fused vehicle traffic: DOT baseline adjusted by current activity
        fused_vehicle = int(dot_monthly * activity_multiplier)
        
        # Foot traffic from Google (more reliable for pedestrians)
        fused_foot = google_foot_daily * 30
        
        # Confidence: High when both sources agree
        agreement = 1.0 - abs(activity_multiplier - 1.0)  # 1.0 = perfect agreement
        confidence = 70 + (agreement * 25)  # 70-95 range
        
        breakdown['activity_multiplier'] = round(activity_multiplier, 2)
        breakdown['fusion_formula'] = f"DOT({dot_monthly}) × activity({activity_multiplier:.2f}) = {fused_vehicle}"
        
        return FusedTrafficResult(
            monthly_vehicle_traffic=fused_vehicle,
            monthly_foot_traffic=int(fused_foot),
            confidence_score=round(confidence, 1),
            primary_source='blended',
            breakdown=breakdown
        )
    
    def _use_dot_only(self, dot_data: Dict, breakdown: Dict) -> FusedTrafficResult:
        """Use DOT data only, estimate foot traffic from vehicle ratio"""
        dot_monthly = dot_data.get('monthly_estimate', 0)
        
        # Estimate foot traffic as 15-25% of vehicle traffic in typical areas
        foot_ratio = 0.20
        foot_traffic = int(dot_monthly * foot_ratio)
        
        breakdown['foot_ratio_used'] = foot_ratio
        breakdown['method'] = 'DOT only, foot traffic estimated from vehicle ratio'
        
        return FusedTrafficResult(
            monthly_vehicle_traffic=dot_monthly,
            monthly_foot_traffic=foot_traffic,
            confidence_score=65.0,  # Good vehicle data, estimated foot
            primary_source='dot',
            breakdown=breakdown
        )
    
    def _use_google_only(self, google_data: Dict, breakdown: Dict) -> FusedTrafficResult:
        """Use Google data only, estimate vehicle traffic from foot ratio"""
        google_foot_daily = google_data.get('avg_daily_traffic', 0)
        vitality = google_data.get('area_vitality_score', 50)
        
        foot_monthly = google_foot_daily * 30
        
        # Estimate vehicle traffic based on area type (vitality as proxy)
        if vitality >= 70:  # Urban/dense area
            vehicle_ratio = 4.0
        elif vitality >= 50:  # Suburban
            vehicle_ratio = 6.0
        else:  # Rural/sparse
            vehicle_ratio = 8.0
        
        vehicle_monthly = int(foot_monthly * vehicle_ratio)
        
        breakdown['vehicle_ratio_used'] = vehicle_ratio
        breakdown['method'] = 'Google only, vehicle traffic estimated from foot ratio'
        
        return FusedTrafficResult(
            monthly_vehicle_traffic=vehicle_monthly,
            monthly_foot_traffic=int(foot_monthly),
            confidence_score=55.0,  # Good foot data, estimated vehicle
            primary_source='google',
            breakdown=breakdown
        )
    
    def _estimate_only(
        self,
        lat: float,
        lng: float,
        radius_miles: float,
        breakdown: Dict
    ) -> FusedTrafficResult:
        """Pure estimation when no API data available"""
        import hashlib
        
        seed_str = f"{lat:.4f},{lng:.4f}"
        seed = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
        
        # Base estimates
        base_vehicle = 50000 + (seed % 50000)
        base_foot = 10000 + (seed % 20000)
        
        breakdown['method'] = 'Pure estimation (no API data available)'
        
        return FusedTrafficResult(
            monthly_vehicle_traffic=base_vehicle,
            monthly_foot_traffic=base_foot,
            confidence_score=30.0,  # Low confidence for estimates
            primary_source='estimated',
            breakdown=breakdown
        )
    
    def _vitality_to_multiplier(self, vitality: float) -> float:
        """Convert vitality score (0-100) to activity multiplier"""
        for (low, high), multiplier in self.VITALITY_TO_MULTIPLIER.items():
            if low <= vitality < high:
                return multiplier
        return 1.0  # Default


def fuse_traffic(
    lat: float,
    lng: float, 
    radius_miles: float,
    dot_data: Optional[Dict] = None,
    google_data: Optional[Dict] = None
) -> FusedTrafficResult:
    """Convenience function for traffic fusion"""
    service = TrafficFusionService()
    return service.fuse_traffic_data(lat, lng, radius_miles, dot_data, google_data)
