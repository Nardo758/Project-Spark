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
            response_message = f"Comparing {', '.join(command.locations)}"
            actions = ["start_comparison"]
        else:
            response_message = "Which locations would you like to compare? Please specify at least two cities or areas."
            actions = ["request_locations"]
    
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
