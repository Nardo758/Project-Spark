"""
OppGrid Foot Traffic API Endpoints
Provides endpoints for collecting and analyzing foot traffic data
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging

from app.db.database import get_db
from app.services.foot_traffic_collector import FootTrafficCollector, check_cached_traffic
from app.services.traffic_analyzer import TrafficAnalyzer
from app.core.dependencies import get_current_user_optional, get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/foot-traffic", tags=["Foot Traffic"])


class CollectAreaRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    radius_miles: float = Field(0.5, ge=0.1, le=2.0)
    place_types: Optional[List[str]] = None
    max_places: int = Field(20, ge=5, le=50)


class AnalyzeAreaRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    radius_meters: int = Field(800, ge=100, le=5000)
    force_refresh: bool = False


class HeatmapRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    radius_meters: int = Field(1000, ge=100, le=5000)


@router.post("/collect/area")
async def collect_area_traffic(
    request: CollectAreaRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Collect foot traffic data for an area from Google Maps Popular Times
    
    This fetches fresh data from SerpAPI and saves to database.
    Cost: ~$0.01-0.05 per area depending on size.
    Requires authentication to prevent cost abuse.
    """
    try:
        collector = FootTrafficCollector(db)
        
        traffic_data = collector.get_area_traffic(
            latitude=request.latitude,
            longitude=request.longitude,
            radius_miles=request.radius_miles,
            place_types=request.place_types or None,
            max_places=request.max_places
        )
        
        saved_count = 0
        if traffic_data:
            saved_count = collector.save_traffic_data(traffic_data)
        
        return {
            "success": True,
            "locations_collected": len(traffic_data),
            "locations_saved": saved_count,
            "center": {
                "latitude": request.latitude,
                "longitude": request.longitude
            },
            "radius_miles": request.radius_miles
        }
        
    except Exception as e:
        logger.error(f"Error collecting area traffic: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/area")
async def analyze_area_traffic(
    request: AnalyzeAreaRequest,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Analyze foot traffic patterns for an area
    
    Returns vitality score, peak times, business density, and traffic patterns.
    Uses cached data if available (< 7 days old).
    """
    try:
        if not request.force_refresh:
            cached = check_cached_traffic(
                db, 
                request.latitude, 
                request.longitude,
                request.radius_meters
            )
            if cached:
                cached['from_cache'] = True
                return cached
        
        analyzer = TrafficAnalyzer(db)
        
        analysis = analyzer.analyze_area_traffic(
            latitude=request.latitude,
            longitude=request.longitude,
            radius_meters=request.radius_meters
        )
        
        analysis['from_cache'] = False
        return analysis
        
    except Exception as e:
        logger.error(f"Error analyzing area traffic: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/opportunity/{opportunity_id}")
async def get_opportunity_traffic(
    opportunity_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Get foot traffic analysis for a specific opportunity
    """
    try:
        analyzer = TrafficAnalyzer(db)
        
        traffic = analyzer.get_opportunity_traffic(opportunity_id)
        
        if not traffic:
            raise HTTPException(
                status_code=404, 
                detail="No traffic data found for this opportunity"
            )
        
        return traffic
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching opportunity traffic: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/opportunity/{opportunity_id}/link")
async def link_opportunity_traffic(
    opportunity_id: int,
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    radius_meters: int = Query(800, ge=100, le=5000),
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Link an opportunity to surrounding foot traffic data
    """
    try:
        analyzer = TrafficAnalyzer(db)
        
        result = analyzer.link_opportunity_traffic(
            opportunity_id=opportunity_id,
            opportunity_lat=latitude,
            opportunity_lng=longitude,
            radius_meters=radius_meters
        )
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail="Could not link traffic data - no data available for this area"
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error linking opportunity traffic: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/heatmap")
async def get_heatmap_data(
    request: HeatmapRequest,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Get foot traffic data formatted for heatmap visualization
    
    Returns GeoJSON FeatureCollection with traffic intensity at each point.
    """
    try:
        analyzer = TrafficAnalyzer(db)
        
        heatmap = analyzer.get_heatmap_data(
            latitude=request.latitude,
            longitude=request.longitude,
            radius_meters=request.radius_meters
        )
        
        return heatmap
        
    except Exception as e:
        logger.error(f"Error getting heatmap data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/collect-and-analyze")
async def collect_and_analyze_traffic(
    request: AnalyzeAreaRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Combined endpoint: Collect fresh data and immediately analyze
    
    Useful for getting traffic analysis for a new area without cached data.
    Requires authentication to prevent cost abuse.
    """
    try:
        if not request.force_refresh:
            cached = check_cached_traffic(
                db, 
                request.latitude, 
                request.longitude,
                request.radius_meters
            )
            if cached and cached.get('total_locations_sampled', 0) > 0:
                cached['from_cache'] = True
                return cached
        
        radius_miles = request.radius_meters / 1609.34
        
        collector = FootTrafficCollector(db)
        traffic_data = collector.get_area_traffic(
            latitude=request.latitude,
            longitude=request.longitude,
            radius_miles=radius_miles,
            max_places=15
        )
        
        if traffic_data:
            collector.save_traffic_data(traffic_data)
        
        analyzer = TrafficAnalyzer(db)
        analysis = analyzer.analyze_area_traffic(
            latitude=request.latitude,
            longitude=request.longitude,
            radius_meters=request.radius_meters
        )
        
        analysis['from_cache'] = False
        analysis['fresh_collection'] = True
        analysis['locations_collected'] = len(traffic_data)
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error in collect-and-analyze: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def foot_traffic_health():
    """Health check for foot traffic service"""
    import os
    serpapi_configured = bool(os.getenv('SERPAPI_KEY'))
    
    return {
        "status": "healthy" if serpapi_configured else "degraded",
        "serpapi_configured": serpapi_configured,
        "message": "Foot traffic service ready" if serpapi_configured else "SERPAPI_KEY not configured"
    }
