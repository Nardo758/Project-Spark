from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.map_data_engine import MapDataEngine

router = APIRouter(prefix="/map", tags=["map"])


class BoundsRequest(BaseModel):
    north: float
    south: float
    east: float
    west: float
    layers: Optional[List[str]] = None


class CityRequest(BaseModel):
    city: str
    state: Optional[str] = None
    layers: Optional[List[str]] = None


class SaveSessionRequest(BaseModel):
    layer_state: Dict[str, bool]
    viewport: Dict[str, Any]
    session_name: Optional[str] = None


@router.get("/layers")
async def get_map_layers(db: Session = Depends(get_db)):
    """Get all available map layers with their configurations"""
    engine = MapDataEngine(db)
    layers = engine.get_all_layers()
    
    if not layers:
        engine.initialize_default_layers()
        layers = engine.get_all_layers()
    
    return {"layers": layers}


@router.post("/layers/initialize")
async def initialize_layers(db: Session = Depends(get_db)):
    """Initialize default map layers"""
    engine = MapDataEngine(db)
    created = engine.initialize_default_layers()
    return {
        "message": f"Initialized {len(created)} layers",
        "layers": [l.layer_name for l in created],
    }


@router.post("/data/bounds")
async def get_map_data_by_bounds(
    request: BoundsRequest,
    db: Session = Depends(get_db),
):
    """
    Get map data for a geographic bounding box.
    Returns pins, heatmap points, and polygons for rendering.
    """
    engine = MapDataEngine(db)
    
    bounds = {
        "north": request.north,
        "south": request.south,
        "east": request.east,
        "west": request.west,
    }
    
    data = engine.get_map_data_for_bounds(
        bounds=bounds,
        layers=request.layers,
    )
    
    return data


@router.post("/data/city")
async def get_map_data_by_city(
    request: CityRequest,
    db: Session = Depends(get_db),
):
    """
    Get map data for a specific city.
    Returns pins, heatmap points, polygons, and computed bounds.
    """
    engine = MapDataEngine(db)
    
    data = engine.get_map_data_for_city(
        city=request.city,
        state=request.state,
        layers=request.layers,
    )
    
    return data


@router.get("/data/city/{city}")
async def get_map_data_city_simple(
    city: str,
    state: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Simple GET endpoint for city map data"""
    engine = MapDataEngine(db)
    return engine.get_map_data_for_city(city=city, state=state)


@router.get("/statistics")
async def get_map_statistics(db: Session = Depends(get_db)):
    """Get statistics about geographic features"""
    engine = MapDataEngine(db)
    return engine.get_layer_statistics()


@router.post("/session")
async def save_map_session(
    request: SaveSessionRequest,
    db: Session = Depends(get_db),
):
    """Save user's map session state"""
    user_id = 1
    
    engine = MapDataEngine(db)
    session = engine.save_user_session(
        user_id=user_id,
        layer_state=request.layer_state,
        viewport=request.viewport,
        session_name=request.session_name,
    )
    
    return {
        "id": session.id,
        "message": "Session saved",
    }


@router.get("/sessions")
async def get_map_sessions(
    limit: int = Query(10, le=50),
    db: Session = Depends(get_db),
):
    """Get user's recent map sessions"""
    user_id = 1
    
    engine = MapDataEngine(db)
    sessions = engine.get_user_sessions(user_id=user_id, limit=limit)
    
    return {"sessions": sessions}
