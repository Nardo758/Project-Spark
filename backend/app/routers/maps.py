from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Any, Literal
import hashlib

from app.db.database import get_db
from app.models.opportunity import Opportunity


router = APIRouter(prefix="/maps", tags=["Maps"])


class HeatmapPoint(BaseModel):
    lat: float
    lng: float
    intensity: float = Field(ge=0.0, le=1.0)


class GeoJSONFeature(BaseModel):
    type: Literal["Feature"] = "Feature"
    geometry: dict[str, Any]
    properties: dict[str, Any] = Field(default_factory=dict)


class MapLayers(BaseModel):
    businesses: list[GeoJSONFeature] = Field(default_factory=list)
    problemHeatmap: list[HeatmapPoint] = Field(default_factory=list)
    neighborhoods: list[GeoJSONFeature] = Field(default_factory=list)


class MapData(BaseModel):
    center: list[float] = Field(min_length=2, max_length=2, description="[lat, lng]")
    zoom: int = Field(ge=1, le=20, default=11)
    layers: MapLayers


class LocationAnalysisResponse(BaseModel):
    query: str | None = None
    mapData: MapData


_KNOWN_CENTERS: dict[str, tuple[float, float]] = {
    "san francisco": (37.7749, -122.4194),
    "sf": (37.7749, -122.4194),
    "miami": (25.7617, -80.1918),
    "new york": (40.7128, -74.0060),
    "nyc": (40.7128, -74.0060),
    "austin": (30.2672, -97.7431),
    "los angeles": (34.0522, -118.2437),
    "la": (34.0522, -118.2437),
    "london": (51.5072, -0.1276),
    "chicago": (41.8781, -87.6298),
    "seattle": (47.6062, -122.3321),
}


def _stable_jitter(lat: float, lng: float, key: str) -> tuple[float, float]:
    """
    Deterministic small offset so multiple points don't overlap.
    This is a placeholder until real lat/lng extraction is stored.
    """
    h = hashlib.sha256(key.encode("utf-8")).digest()
    a = int.from_bytes(h[:2], "big") / 65535.0  # 0..1
    b = int.from_bytes(h[2:4], "big") / 65535.0
    # ~ +/- 0.04 degrees (~4-5km depending on latitude)
    dlat = (a - 0.5) * 0.08
    dlng = (b - 0.5) * 0.08
    return (lat + dlat, lng + dlng)


def _pick_center(query: str | None) -> tuple[float, float]:
    if not query:
        return _KNOWN_CENTERS["san francisco"]
    q = query.strip().lower()
    for k, center in _KNOWN_CENTERS.items():
        if k in q:
            return center
    return _KNOWN_CENTERS["san francisco"]


@router.get("/location-analysis", response_model=LocationAnalysisResponse)
def location_analysis(
    q: str | None = Query(default=None, description="Free-text location query (e.g. 'Retail in Miami')"),
    limit: int = Query(default=200, ge=1, le=1000),
    db: Session = Depends(get_db),
) -> LocationAnalysisResponse:
    """
    Returns a multi-layer `mapData` response suitable for a side-by-side comparison view.

    Note: The current OppGrid schema stores city/region/country but not precise coordinates.
    Until geographic extraction is fully implemented, coordinates are approximated with a
    deterministic jitter around a query-selected city center.
    """
    center_lat, center_lng = _pick_center(q)

    opps = (
        db.query(Opportunity)
        .filter(Opportunity.status == "active")
        .order_by(Opportunity.validation_count.desc(), Opportunity.created_at.desc())
        .limit(limit)
        .all()
    )

    businesses: list[GeoJSONFeature] = []
    heat: list[HeatmapPoint] = []

    for opp in opps:
        # Placeholder: infer layer from source platform.
        platform = (opp.source_platform or "").lower()
        lat, lng = _stable_jitter(center_lat, center_lng, f"{opp.id}:{opp.city}:{opp.region}:{opp.country}")

        if platform in {"google_maps", "google", "yelp"}:
            businesses.append(
                GeoJSONFeature(
                    geometry={"type": "Point", "coordinates": [lng, lat]},
                    properties={
                        "source": platform or "unknown",
                        "name": opp.title,
                        "rating": None,
                        "popupContent": (opp.ai_summary or opp.description or "")[:240],
                        "opportunityId": opp.id,
                    },
                )
            )
        else:
            # Treat everything else as a "problem signal" point for now.
            intensity = 0.2
            if opp.validation_count:
                intensity = min(1.0, max(0.2, opp.validation_count / 100.0))
            heat.append(HeatmapPoint(lat=lat, lng=lng, intensity=float(intensity)))

    map_data = MapData(
        center=[float(center_lat), float(center_lng)],
        zoom=11,
        layers=MapLayers(businesses=businesses, problemHeatmap=heat, neighborhoods=[]),
    )
    return LocationAnalysisResponse(query=q, mapData=map_data)


class LayerCommandRequest(BaseModel):
    prompt: str
    current_center: dict[str, float] | None = None
    current_radius: float = 1.0
    active_layers: list[str] = Field(default_factory=list)


class LayerAction(BaseModel):
    action: str
    layer_type: str | None = None
    config: dict[str, Any] | None = None
    center: dict[str, float] | None = None
    address: str | None = None
    radius: float | None = None


class LayerCommandResponse(BaseModel):
    actions: list[LayerAction]
    message: str | None = None


SUPPORTED_LAYER_TYPES = {"center_point", "deep_clone", "demographics", "competition", "traffic"}

LAYER_KEYWORDS: dict[str, list[str]] = {
    "demographics": ["demographics", "population", "income", "census", "people", "age", "household"],
    "competition": ["competition", "competitors", "competitor", "nearby", "similar", "businesses", "rivals"],
    "deep_clone": ["clone", "copy", "replicate", "franchise", "model", "template"],
    "traffic": ["traffic", "footfall", "foot traffic", "busy", "transit", "pedestrian"],
}

RADIUS_KEYWORDS: dict[str, float] = {
    "quarter mile": 0.25, "0.25 mile": 0.25, "0.25mi": 0.25,
    "half mile": 0.5, "0.5 mile": 0.5, "0.5mi": 0.5,
    "1 mile": 1.0, "one mile": 1.0, "1mi": 1.0,
    "2 mile": 2.0, "two mile": 2.0, "2mi": 2.0,
    "3 mile": 3.0, "three mile": 3.0, "3mi": 3.0,
    "5 mile": 5.0, "five mile": 5.0, "5mi": 5.0,
    "10 mile": 10.0, "ten mile": 10.0, "10mi": 10.0,
}

BUSINESS_TYPES = ["coffee", "restaurant", "gym", "pizza", "cafe", "shop", "store", "bakery", "bar", "salon", "spa"]


CITY_DISPLAY_NAMES: dict[str, str] = {
    "sf": "San Francisco",
    "nyc": "New York City",
    "la": "Los Angeles",
}


def _parse_center(prompt_lower: str) -> LayerAction | None:
    """Extract center location from prompt."""
    for city, coords in _KNOWN_CENTERS.items():
        if city in prompt_lower:
            display_name = CITY_DISPLAY_NAMES.get(city, city.title())
            return LayerAction(
                action="set_center",
                center={"lat": coords[0], "lng": coords[1]},
                address=display_name
            )
    return None


def _parse_radius(prompt_lower: str) -> LayerAction | None:
    """Extract radius from prompt."""
    for keyword, radius in RADIUS_KEYWORDS.items():
        if keyword in prompt_lower:
            return LayerAction(action="set_radius", radius=radius)
    return None


def _parse_layers(prompt_lower: str, active_layers: list[str]) -> list[LayerAction]:
    """Extract layer actions from prompt."""
    actions: list[LayerAction] = []
    
    for layer_type, keywords in LAYER_KEYWORDS.items():
        if layer_type in active_layers:
            continue
        for keyword in keywords:
            if keyword in prompt_lower:
                config: dict[str, Any] = {}
                if layer_type == "competition":
                    for word in BUSINESS_TYPES:
                        if word in prompt_lower:
                            config["searchQuery"] = word
                            break
                actions.append(LayerAction(
                    action="add_layer",
                    layer_type=layer_type,
                    config=config if config else None
                ))
                break
    
    return actions


@router.post("/parse-layer-command", response_model=LayerCommandResponse)
async def parse_layer_command(request: LayerCommandRequest):
    """Parse natural language prompt into layer actions.
    
    Supports:
    - Setting center point to known cities (Austin, NYC, SF, etc.)
    - Setting radius (0.25 to 10 miles)
    - Adding layers (demographics, competition, deep_clone, traffic)
    - Configuring competition search queries
    """
    prompt_lower = request.prompt.lower().strip()
    
    if not prompt_lower:
        return LayerCommandResponse(
            actions=[],
            message="Please provide a description of what you'd like to see on the map."
        )
    
    actions: list[LayerAction] = []
    
    center_action = _parse_center(prompt_lower)
    if center_action:
        actions.append(center_action)
    
    radius_action = _parse_radius(prompt_lower)
    if radius_action:
        actions.append(radius_action)
    
    layer_actions = _parse_layers(prompt_lower, request.active_layers)
    actions.extend(layer_actions)
    
    if not actions:
        suggestions = [
            "Try mentioning a city name (Austin, NYC, Miami, etc.)",
            "Specify a radius like '1 mile' or '5 miles'",
            "Ask for layers: demographics, competition, traffic, or clone"
        ]
        return LayerCommandResponse(
            actions=[],
            message=f"I couldn't understand that request. {suggestions[0]}. {suggestions[1]}. {suggestions[2]}."
        )
    
    action_descriptions = []
    for action in actions:
        if action.action == "set_center":
            action_descriptions.append(f"center to {action.address}")
        elif action.action == "set_radius":
            action_descriptions.append(f"{action.radius} mile radius")
        elif action.action == "add_layer":
            action_descriptions.append(f"add {action.layer_type} layer")
    
    message = f"Applied: {', '.join(action_descriptions)}"
    
    return LayerCommandResponse(
        actions=actions,
        message=message
    )
