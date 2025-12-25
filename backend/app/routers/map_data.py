from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.map_data_engine import MapDataEngine
from app.services.census_service import census_service

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


@router.get("/census/population/{state_fips}/{county_fips}")
async def get_population_dynamics(
    state_fips: str,
    county_fips: str,
):
    """
    Get comprehensive population dynamics for a county.
    
    Returns current population, historical trends (2019-2024), 
    migration patterns, and demographic data.
    
    Args:
        state_fips: 2-digit state FIPS code (e.g., "48" for Texas)
        county_fips: 3-digit county FIPS code (e.g., "015" for Austin County)
    """
    if not census_service.is_configured:
        raise HTTPException(
            status_code=503,
            detail="Census API key not configured. Please add CENSUS_API_KEY to environment variables."
        )
    
    data = await census_service.get_population_dynamics(state_fips, county_fips)
    
    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"No population data found for county {state_fips}-{county_fips}"
        )
    
    return data


@router.get("/census/population-estimates")
async def get_population_estimates(
    state_fips: Optional[str] = Query(None, description="2-digit state FIPS code"),
    county_fips: Optional[str] = Query(None, description="3-digit county FIPS code"),
    year: int = Query(2024, description="Data year (2019-2024)"),
):
    """
    Get population estimates with migration components.
    
    Returns population, births, deaths, domestic/international migration.
    If no state specified, returns all US counties (large response).
    """
    if not census_service.is_configured:
        raise HTTPException(
            status_code=503,
            detail="Census API key not configured"
        )
    
    data = await census_service.fetch_population_estimates(state_fips, county_fips, year)
    
    if not data:
        raise HTTPException(
            status_code=404,
            detail="No population estimates found for the specified geography"
        )
    
    return {"year": year, "data": data, "count": len(data)}


@router.get("/census/migration/{state_fips}/{county_fips}")
async def get_migration_flows(
    state_fips: str,
    county_fips: str,
    year: int = Query(2022, description="Data year (latest: 2022)"),
):
    """
    Get county-to-county migration flows.
    
    Returns where people are moving from (top 20 origins),
    total moved in/out, and net migration.
    """
    if not census_service.is_configured:
        raise HTTPException(
            status_code=503,
            detail="Census API key not configured"
        )
    
    data = await census_service.fetch_migration_flows(state_fips, county_fips, year)
    
    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"No migration flow data found for county {state_fips}-{county_fips}"
        )
    
    return data


@router.get("/census/demographics/{state_fips}/{county_fips}")
async def get_county_demographics(
    state_fips: str,
    county_fips: str,
):
    """
    Get ACS 5-Year demographic data for a county.
    
    Returns population, income, education, housing, and economic indicators.
    """
    if not census_service.is_configured:
        raise HTTPException(
            status_code=503,
            detail="Census API key not configured"
        )
    
    data = await census_service.fetch_by_county(state_fips, county_fips)
    
    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"No demographic data found for county {state_fips}-{county_fips}"
        )
    
    return data


@router.get("/census/extended/{state_fips}/{county_fips}")
async def get_county_extended_demographics(
    state_fips: str,
    county_fips: str,
):
    """
    Get extended demographic data for a county.
    
    Includes income distribution (16 brackets), age distribution,
    commute patterns, internet access, and housing tenure.
    """
    if not census_service.is_configured:
        raise HTTPException(
            status_code=503,
            detail="Census API key not configured"
        )
    
    data = await census_service.fetch_extended_demographics(state_fips, county_fips)
    
    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"No extended demographic data found for county {state_fips}-{county_fips}"
        )
    
    return data


@router.get("/census/status")
async def get_census_api_status():
    """Check if Census API is configured and available."""
    return {
        "configured": census_service.is_configured,
        "message": "Census API ready" if census_service.is_configured else "CENSUS_API_KEY not set"
    }
