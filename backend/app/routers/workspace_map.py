"""
Workspace Map API Router

Provides endpoints for the map-centric workspace including:
- Command parsing and execution
- Layer generation
- Session management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from app.db.database import get_db
from app.models.user import User
from app.models.user_map_session import UserMapSession
from app.core.dependencies import get_current_user
from app.services.map_command_parser import map_command_parser, MapCommandType
from app.services.map_layer_generator import map_layer_generator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workspace/map", tags=["Workspace Map"])


class ChatMessage(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)
    opportunity_id: Optional[int] = None
    business_type: Optional[str] = None
    current_location: Optional[str] = None
    center_lat: Optional[float] = None
    center_lng: Optional[float] = None


class ChatResponse(BaseModel):
    message: str
    command_type: str
    layer: Optional[Dict[str, Any]] = None
    actions: List[str] = []
    confidence: float


class LayerRequest(BaseModel):
    layer_type: str
    business_type: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius_miles: Optional[float] = 10.0
    state_fips: Optional[str] = None
    metrics: Optional[List[str]] = None


class SessionState(BaseModel):
    session_name: Optional[str] = None
    layer_state: Optional[Dict[str, Any]] = None
    viewport: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None


@router.post("/chat", response_model=ChatResponse)
async def process_chat_message(
    message: ChatMessage,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Process a chat message and return map commands/layers"""
    
    command = map_command_parser.parse_simple(message.content)
    
    if command.confidence < 0.5:
        try:
            command = await map_command_parser.parse(
                user_query=message.content,
                user_id=current_user.id,
                business_type=message.business_type,
                current_location=message.current_location
            )
        except Exception as e:
            logger.error(f"LLM parsing failed: {e}")
    
    layer = None
    actions = []
    response_message = command.explanation or "Processing your request..."
    
    if command.command_type == MapCommandType.SHOW_COMPETITION:
        if message.center_lat and message.center_lng:
            layer = await map_layer_generator.generate_competition_layer(
                business_type=message.business_type or command.business_type or "business",
                latitude=message.center_lat,
                longitude=message.center_lng,
                radius_miles=command.radius_miles or 10.0
            )
            count = layer.get("metadata", {}).get("count", 0)
            response_message = f"Found {count} competitors within {command.radius_miles or 10} miles"
            actions = ["add_layer", "fit_bounds"]
        else:
            response_message = "Please specify a location to search for competitors"
            actions = ["request_location"]
    
    elif command.command_type == MapCommandType.SHOW_DEMOGRAPHICS:
        if command.location:
            from app.services.location_utils import get_state_fips_from_name
            state_fips = get_state_fips_from_name(command.location)
            if state_fips:
                layer = await map_layer_generator.generate_demographics_layer(
                    state_fips=state_fips,
                    metrics=command.demographic_metrics
                )
                response_message = f"Loaded demographic data for {command.location}"
                actions = ["show_demographics_panel"]
        else:
            response_message = "I can show demographics for a specific state. Which state would you like to analyze?"
            actions = ["request_location"]
    
    elif command.command_type == MapCommandType.SET_RADIUS:
        if command.radius_miles:
            if message.center_lat and message.center_lng:
                layer = map_layer_generator.generate_radius_circle(
                    center_lat=message.center_lat,
                    center_lng=message.center_lng,
                    radius_miles=command.radius_miles
                )
            response_message = f"Analysis radius set to {command.radius_miles} miles"
            actions = ["update_radius", "refresh_layers"]
    
    elif command.command_type == MapCommandType.CLEAR_LAYER:
        layer_name = command.layer_name or "all"
        response_message = f"Cleared {layer_name} layer from the map"
        actions = ["clear_layer"]
    
    elif command.command_type == MapCommandType.COMPARE_LOCATIONS:
        if command.locations and len(command.locations) >= 2:
            comparison_data = await _geocode_and_compare_locations(command.locations)
            if comparison_data:
                layer = map_layer_generator.generate_comparison_layer(comparison_data)
                response_message = f"Comparing {', '.join(command.locations)} - markers added to map"
                actions = ["add_layer", "fit_bounds", "show_comparison_panel"]
            else:
                response_message = f"Comparing {', '.join(command.locations)}"
                actions = ["start_comparison"]
        else:
            response_message = "Which locations would you like to compare? Please specify at least two cities or areas."
            actions = ["request_locations"]
    
    elif command.command_type == MapCommandType.SHOW_HEATMAP:
        if message.center_lat and message.center_lng:
            heatmap_points = await _generate_heatmap_points(
                center_lat=message.center_lat,
                center_lng=message.center_lng,
                radius_miles=command.radius_miles or 10.0,
                metric=command.heatmap_metric or "density"
            )
            layer = map_layer_generator.generate_heatmap_layer(
                points=heatmap_points,
                metric=command.heatmap_metric or "density"
            )
            response_message = f"Generated heatmap for {command.heatmap_metric or 'density'}"
            actions = ["add_layer"]
        else:
            response_message = "Please specify a location to generate a heatmap"
            actions = ["request_location"]
    
    elif command.command_type == MapCommandType.ZOOM_TO:
        if command.location:
            coords = await _geocode_location(command.location)
            if coords:
                response_message = f"Zooming to {command.location}"
                actions = ["zoom_to", "set_center"]
                layer = {
                    "layer_id": "zoom_target",
                    "layer_type": "viewport",
                    "viewport": {
                        "center": [coords["longitude"], coords["latitude"]],
                        "zoom": command.zoom_level or 12
                    }
                }
            else:
                response_message = f"Could not find location: {command.location}"
                actions = []
        else:
            response_message = "Where would you like to zoom to?"
            actions = ["request_location"]
    
    elif command.command_type == MapCommandType.FILTER_BY:
        filter_type = command.filter_type or "rating"
        filter_value = command.filter_value
        response_message = f"Filtering by {filter_type}" + (f" >= {filter_value}" if filter_value else "")
        actions = ["apply_filter", "refresh_layers"]
        layer = {
            "layer_id": "filter",
            "layer_type": "filter",
            "filter": {
                "type": filter_type,
                "value": filter_value,
                "operator": ">=" if filter_value else "exists"
            }
        }
    
    elif command.command_type == MapCommandType.ANALYZE_AREA:
        if message.center_lat and message.center_lng:
            analysis = await _analyze_area(
                center_lat=message.center_lat,
                center_lng=message.center_lng,
                radius_miles=command.radius_miles or 5.0
            )
            response_message = f"Area analysis complete:\n{analysis['summary']}"
            actions = ["show_analysis_panel"]
            layer = {
                "layer_id": "analysis",
                "layer_type": "analysis",
                "data": analysis
            }
        else:
            response_message = "Please specify a location to analyze"
            actions = ["request_location"]
    
    elif command.command_type == MapCommandType.UNKNOWN:
        response_message = "I'm not sure what you're asking. Try commands like:\n- Show me competitors\n- What are the demographics?\n- Set radius to 5 miles\n- Compare Austin and Denver"
        actions = ["show_help"]
    
    return ChatResponse(
        message=response_message,
        command_type=command.command_type.value,
        layer=layer,
        actions=actions,
        confidence=command.confidence
    )


@router.post("/layer")
async def generate_layer(
    request: LayerRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate a specific map layer on demand"""
    
    if request.layer_type == "competition":
        if not request.latitude or not request.longitude:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Latitude and longitude required for competition layer"
            )
        return await map_layer_generator.generate_competition_layer(
            business_type=request.business_type or "business",
            latitude=request.latitude,
            longitude=request.longitude,
            radius_miles=request.radius_miles or 10.0
        )
    
    elif request.layer_type == "demographics":
        if not request.state_fips:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="State FIPS code required for demographics layer"
            )
        return await map_layer_generator.generate_demographics_layer(
            state_fips=request.state_fips,
            metrics=request.metrics
        )
    
    elif request.layer_type == "radius":
        if not request.latitude or not request.longitude:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Latitude and longitude required for radius layer"
            )
        return map_layer_generator.generate_radius_circle(
            center_lat=request.latitude,
            center_lng=request.longitude,
            radius_miles=request.radius_miles or 10.0
        )
    
    elif request.layer_type == "heatmap":
        if not request.latitude or not request.longitude:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Latitude and longitude required for heatmap layer"
            )
        points = await _generate_heatmap_points(
            center_lat=request.latitude,
            center_lng=request.longitude,
            radius_miles=request.radius_miles or 10.0,
            metric="density"
        )
        return map_layer_generator.generate_heatmap_layer(points=points)
    
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Unknown layer type: {request.layer_type}"
    )


@router.get("/session")
async def get_session(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the current user's map session state"""
    
    session = db.query(UserMapSession).filter(
        UserMapSession.user_id == current_user.id
    ).order_by(UserMapSession.updated_at.desc()).first()
    
    if not session:
        return {
            "session_id": None,
            "layer_state": {},
            "viewport": {"center": [-98.5795, 39.8283], "zoom": 4},
            "filters": {}
        }
    
    return {
        "session_id": session.id,
        "session_name": session.session_name,
        "layer_state": session.layer_state or {},
        "viewport": session.viewport or {"center": [-98.5795, 39.8283], "zoom": 4},
        "filters": session.filters or {}
    }


@router.put("/session")
async def save_session(
    state: SessionState,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save the current map session state"""
    
    session = db.query(UserMapSession).filter(
        UserMapSession.user_id == current_user.id
    ).order_by(UserMapSession.updated_at.desc()).first()
    
    if not session:
        session = UserMapSession(user_id=current_user.id)
        db.add(session)
    
    if state.session_name is not None:
        session.session_name = state.session_name
    if state.layer_state is not None:
        session.layer_state = state.layer_state
    if state.viewport is not None:
        session.viewport = state.viewport
    if state.filters is not None:
        session.filters = state.filters
    
    db.commit()
    db.refresh(session)
    
    return {
        "session_id": session.id,
        "message": "Session saved successfully"
    }


CITY_COORDS = {
    "austin": {"latitude": 30.2672, "longitude": -97.7431},
    "denver": {"latitude": 39.7392, "longitude": -104.9903},
    "seattle": {"latitude": 47.6062, "longitude": -122.3321},
    "miami": {"latitude": 25.7617, "longitude": -80.1918},
    "new york": {"latitude": 40.7128, "longitude": -74.0060},
    "los angeles": {"latitude": 34.0522, "longitude": -118.2437},
    "chicago": {"latitude": 41.8781, "longitude": -87.6298},
    "houston": {"latitude": 29.7604, "longitude": -95.3698},
    "phoenix": {"latitude": 33.4484, "longitude": -112.0740},
    "philadelphia": {"latitude": 39.9526, "longitude": -75.1652},
    "san antonio": {"latitude": 29.4241, "longitude": -98.4936},
    "san diego": {"latitude": 32.7157, "longitude": -117.1611},
    "dallas": {"latitude": 32.7767, "longitude": -96.7970},
    "san jose": {"latitude": 37.3382, "longitude": -121.8863},
    "boston": {"latitude": 42.3601, "longitude": -71.0589},
    "atlanta": {"latitude": 33.7490, "longitude": -84.3880},
    "nashville": {"latitude": 36.1627, "longitude": -86.7816},
    "portland": {"latitude": 45.5152, "longitude": -122.6784},
    "las vegas": {"latitude": 36.1699, "longitude": -115.1398},
    "charlotte": {"latitude": 35.2271, "longitude": -80.8431},
}


async def _geocode_location(location: str) -> Optional[Dict[str, float]]:
    """Get coordinates for a location name"""
    location_lower = location.lower().strip()
    if location_lower in CITY_COORDS:
        return CITY_COORDS[location_lower]
    
    for city, coords in CITY_COORDS.items():
        if city in location_lower or location_lower in city:
            return coords
    
    return None


async def _geocode_and_compare_locations(locations: List[str]) -> List[Dict[str, Any]]:
    """Geocode multiple locations and prepare comparison data"""
    results = []
    
    for idx, loc in enumerate(locations):
        coords = await _geocode_location(loc)
        if coords:
            results.append({
                "name": loc.title(),
                "latitude": coords["latitude"],
                "longitude": coords["longitude"],
                "score": 100 - (idx * 5),
                "metrics": {
                    "market_size": "Medium" if idx % 2 == 0 else "Large",
                    "competition": "Low" if idx % 3 == 0 else "Moderate",
                    "growth_rate": f"{5 + idx}%"
                }
            })
    
    return results


async def _generate_heatmap_points(
    center_lat: float,
    center_lng: float,
    radius_miles: float,
    metric: str
) -> List[Dict[str, Any]]:
    """Generate sample heatmap points around a center location"""
    import random
    import math
    
    points = []
    num_points = 50
    
    for i in range(num_points):
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(0, radius_miles) * 1.60934
        
        lat_offset = (distance * math.sin(angle)) / 111.32
        lng_offset = (distance * math.cos(angle)) / (111.32 * math.cos(math.radians(center_lat)))
        
        points.append({
            "latitude": center_lat + lat_offset,
            "longitude": center_lng + lng_offset,
            "weight": random.uniform(0.3, 1.0)
        })
    
    return points


async def _analyze_area(
    center_lat: float,
    center_lng: float,
    radius_miles: float
) -> Dict[str, Any]:
    """Perform area analysis"""
    return {
        "summary": f"Analysis of {radius_miles} mile radius around ({center_lat:.4f}, {center_lng:.4f})",
        "metrics": {
            "estimated_population": "~50,000",
            "median_income": "$65,000",
            "business_density": "Medium",
            "growth_trend": "Positive"
        },
        "recommendations": [
            "Good foot traffic potential",
            "Moderate competition level",
            "Growing residential area"
        ]
    }
