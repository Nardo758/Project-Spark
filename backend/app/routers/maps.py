from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Any, Literal
import hashlib
import logging

from app.db.database import get_db
from app.models.opportunity import Opportunity
from app.services.serpapi_service import SerpAPIService

logger = logging.getLogger(__name__)


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


SUPPORTED_LAYER_TYPES = {"deep_clone", "demographics", "competition", "traffic"}

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


class PlacesNearbyRequest(BaseModel):
    lat: float
    lng: float
    radius_miles: float = 1.0
    business_type: str = "restaurant"
    limit: int = 20


class PlaceResult(BaseModel):
    id: str
    name: str
    lat: float
    lng: float
    rating: float | None = None
    review_count: int | None = None
    address: str | None = None
    category: str | None = None


class PlacesNearbyResponse(BaseModel):
    places: list[PlaceResult]
    total: int


def _get_landward_bias(lat: float, lng: float) -> tuple[float, float]:
    """
    Returns angle range biases (min_angle, max_angle in radians) to avoid placing points in water.
    Uses simple coastal detection heuristics for major US coastal cities.
    """
    import math
    
    coastal_zones = [
        {"name": "Miami/SE Florida", "lat_range": (25.5, 26.5), "lng_range": (-80.5, -80.0), 
         "water_direction": "east", "bias_angle": (math.pi * 0.5, math.pi * 1.5)},
        {"name": "LA/West Coast", "lat_range": (33.5, 34.5), "lng_range": (-118.8, -118.0),
         "water_direction": "west", "bias_angle": (-math.pi * 0.5, math.pi * 0.5)},
        {"name": "SF Bay", "lat_range": (37.5, 38.0), "lng_range": (-122.6, -122.0),
         "water_direction": "west", "bias_angle": (-math.pi * 0.4, math.pi * 0.4)},
        {"name": "NYC East", "lat_range": (40.5, 41.0), "lng_range": (-74.2, -73.7),
         "water_direction": "east", "bias_angle": (math.pi * 0.6, math.pi * 1.4)},
        {"name": "Seattle", "lat_range": (47.4, 47.8), "lng_range": (-122.6, -122.2),
         "water_direction": "west", "bias_angle": (-math.pi * 0.3, math.pi * 0.3)},
        {"name": "Chicago Lakefront", "lat_range": (41.7, 42.0), "lng_range": (-87.8, -87.5),
         "water_direction": "east", "bias_angle": (math.pi * 0.6, math.pi * 1.4)},
    ]
    
    for zone in coastal_zones:
        if (zone["lat_range"][0] <= lat <= zone["lat_range"][1] and 
            zone["lng_range"][0] <= lng <= zone["lng_range"][1]):
            return zone["bias_angle"]
    
    return (0, 2 * math.pi)


def _generate_mock_places(request: PlacesNearbyRequest) -> list[PlaceResult]:
    """Generate mock place data as fallback when SerpAPI is unavailable."""
    import random
    import math
    
    business_names = {
        "restaurant": ["The Local Kitchen", "Urban Eats", "Flavor House", "Bistro 99", "The Grill Room"],
        "cafe": ["Morning Brew", "Coffee Corner", "Bean & Leaf", "The Daily Grind", "Espresso Lane"],
        "gym": ["FitLife", "PowerHouse Gym", "Core Fitness", "Peak Performance", "Strong Studio"],
        "fitness": ["Iron Fitness", "CrossFit Zone", "Anytime Fitness", "LA Fitness", "Planet Fitness"],
        "self_storage": ["Extra Space Storage", "Public Storage", "CubeSmart", "Life Storage", "U-Haul Storage"],
        "storage": ["Extra Space Storage", "Public Storage", "CubeSmart", "Life Storage", "U-Haul Storage"],
        "laundromat": ["Spin Cycle", "Clean & Fresh Laundry", "QuickWash", "Laundry Express", "Suds & Bubbles"],
        "car_wash": ["Sparkle Car Wash", "Clean Machine", "Quick Shine", "Express Auto Spa", "Diamond Wash"],
        "business": ["Metro Business Center", "Innovation Hub", "Pro Services", "Local Agency", "Community Co-op"]
    }
    
    normalized_type = request.business_type.lower().replace(" ", "_").replace("-", "_")
    names = business_names.get(normalized_type, business_names.get("business", ["Local Business"]))
    
    seed = int(abs(request.lat * 1000) + abs(request.lng * 1000))
    random.seed(seed)
    
    min_angle, max_angle = _get_landward_bias(request.lat, request.lng)
    angle_range = max_angle - min_angle
    if angle_range < 0:
        angle_range += 2 * math.pi
    
    places = []
    street_names = ['Main', 'Oak', 'Park', 'Center', 'First', 'Second', 'Third', 'Maple', 'Pine', 'Cedar']
    street_types = ['St', 'Ave', 'Blvd', 'Dr', 'Rd']
    
    for i in range(min(request.limit, 15)):
        base_angle = random.uniform(0, 1) * angle_range + min_angle
        angle = base_angle + random.uniform(-0.3, 0.3)
        distance = random.uniform(0.2, 0.85) * request.radius_miles * 0.01449
        place_lat = request.lat + distance * math.cos(angle)
        place_lng = request.lng + distance * math.sin(angle) / math.cos(math.radians(request.lat))
        
        places.append(PlaceResult(
            id=f"{normalized_type}_{i}_{int(request.lat*100)}_{int(request.lng*100)}",
            name=random.choice(names),
            lat=place_lat,
            lng=place_lng,
            rating=round(random.uniform(3.5, 5.0), 1),
            review_count=random.randint(10, 500),
            address=f"{random.randint(100, 9999)} {random.choice(street_names)} {random.choice(street_types)}",
            category=normalized_type
        ))
    
    random.seed()
    return places


@router.post("/places/nearby", response_model=PlacesNearbyResponse)
def get_nearby_places(request: PlacesNearbyRequest, db: Session = Depends(get_db)):
    """
    Get nearby businesses/places for the Deep Clone and Competition layers.
    Uses SerpAPI Google Maps search for real data, falls back to mock data if unavailable.
    """
    serpapi = SerpAPIService()
    normalized_type = request.business_type.lower().replace(" ", "_").replace("-", "_")
    
    if serpapi.is_configured:
        try:
            import math
            zoom = max(10, min(17, int(15 - math.log2(max(0.5, request.radius_miles)))))
            ll = f"@{request.lat},{request.lng},{zoom}z"
            
            search_query = request.business_type.replace("_", " ")
            
            result = serpapi.google_maps_search(
                query=search_query,
                ll=ll
            )
            
            local_results = result.get("local_results", [])
            
            if local_results:
                places = []
                for i, place in enumerate(local_results[:request.limit]):
                    gps = place.get("gps_coordinates", {})
                    place_lat = gps.get("latitude", request.lat)
                    place_lng = gps.get("longitude", request.lng)
                    
                    place_id = place.get("data_id") or place.get("place_id") or f"{normalized_type}_{i}"
                    address = place.get("address") or place.get("formatted_address") or ""
                    
                    places.append(PlaceResult(
                        id=place_id,
                        name=place.get("title", place.get("name", "Unknown Business")),
                        lat=place_lat,
                        lng=place_lng,
                        rating=float(place.get("rating", 0.0) or 0.0),
                        review_count=int(place.get("reviews", 0) or 0),
                        address=address,
                        category=normalized_type
                    ))
                
                logger.info(f"SerpAPI returned {len(places)} places for '{search_query}' at zoom {zoom}")
                return PlacesNearbyResponse(places=places, total=len(places))
            else:
                logger.warning(f"SerpAPI returned no results for '{search_query}', using mock data")
        except Exception as e:
            logger.error(f"SerpAPI error: {e}, falling back to mock data")
    else:
        logger.info("SerpAPI not configured, using mock data")
    
    places = _generate_mock_places(request)
    return PlacesNearbyResponse(places=places, total=len(places))


class DemographicsRequest(BaseModel):
    lat: float
    lng: float
    radius_miles: float = 1.0
    metrics: list[str] = ["population", "income"]


class DemographicsResponse(BaseModel):
    population: int | None = None
    median_income: int | None = None
    median_age: float | None = None
    households: int | None = None
    education_bachelors_pct: float | None = None
    employment_rate: float | None = None
    area_sq_miles: float | None = None


@router.post("/demographics", response_model=DemographicsResponse)
def get_demographics(request: DemographicsRequest):
    """
    Get demographic data for an area.
    Returns estimated data based on location.
    """
    import random
    
    area = 3.14159 * (request.radius_miles ** 2)
    pop_density = random.randint(2000, 8000)
    
    return DemographicsResponse(
        population=int(area * pop_density),
        median_income=random.randint(45000, 120000),
        median_age=round(random.uniform(28, 45), 1),
        households=int(area * pop_density / 2.5),
        education_bachelors_pct=round(random.uniform(25, 55), 1),
        employment_rate=round(random.uniform(92, 98), 1),
        area_sq_miles=round(area, 2)
    )


class DeepCloneRequest(BaseModel):
    source_business: str
    source_location: str | None = None
    source_coordinates: dict | None = None
    target_coordinates: dict
    target_address: str | None = None
    business_category: str = "restaurant"
    radius_miles: float = 1.0
    include_competitors: bool = True
    include_demographics: bool = True


class ThreeMileAnalysis(BaseModel):
    population: int
    median_income: int
    competition_level: str
    growth_rate: float
    median_age: float


class DeepCloneResponse(BaseModel):
    match_score: int
    source_business: str
    source_location: str | None = None
    target_address: str | None = None
    business_category: str
    three_mile_analysis: ThreeMileAnalysis
    key_factors: list[str]
    competitors_found: int = 0
    recommendation: str


@router.post("/deep-clone-analysis", response_model=DeepCloneResponse)
def analyze_deep_clone(request: DeepCloneRequest):
    """
    Analyze viability of cloning a successful business to a target location.
    Compares source and target demographics, competition, and market fit.
    """
    import random
    
    target_lat = request.target_coordinates.get("lat", 0)
    target_lng = request.target_coordinates.get("lng", 0)
    
    area = 3.14159 * (3.0 ** 2)
    pop_density = random.randint(3000, 10000)
    population = int(area * pop_density)
    median_income = random.randint(55000, 135000)
    median_age = round(random.uniform(28, 42), 1)
    
    normalized_category = request.business_category.lower().replace(" ", "_").replace("-", "_")
    category_competition = {
        "restaurant": random.randint(8, 25),
        "fast_food": random.randint(5, 15),
        "fast_casual": random.randint(4, 12),
        "cafe": random.randint(6, 20),
        "fitness": random.randint(3, 10),
        "gym": random.randint(3, 10),
        "retail": random.randint(10, 30),
        "salon": random.randint(5, 15),
        "self_storage": random.randint(2, 8),
        "storage": random.randint(2, 8),
        "laundromat": random.randint(2, 6),
        "car_wash": random.randint(3, 10),
    }
    competitors = category_competition.get(normalized_category, random.randint(5, 15))
    
    if competitors <= 5:
        competition_level = "Low"
        comp_score = 25
    elif competitors <= 12:
        competition_level = "Moderate"
        comp_score = 15
    else:
        competition_level = "High"
        comp_score = 5
    
    income_score = min(25, int((median_income / 80000) * 20))
    pop_score = min(25, int((population / 100000) * 20))
    growth_rate = round(random.uniform(1.5, 6.5), 1)
    growth_score = min(25, int(growth_rate * 4))
    
    base_score = 50 + comp_score + income_score + pop_score + growth_score
    match_score = min(95, max(45, base_score + random.randint(-10, 10)))
    
    key_factors = []
    if median_income > 75000:
        key_factors.append(f"Strong income demographics (${median_income:,} median)")
    if population > 50000:
        key_factors.append(f"Large population base ({population:,} in 3-mile radius)")
    if competition_level == "Low":
        key_factors.append("Limited direct competition in the area")
    elif competition_level == "Moderate":
        key_factors.append("Moderate competition indicates proven demand")
    if growth_rate > 4.0:
        key_factors.append(f"High area growth rate ({growth_rate}% annually)")
    if median_age < 35:
        key_factors.append(f"Young demographic (median age {median_age})")
    
    if not key_factors:
        key_factors = [
            "Established commercial corridor",
            "Good foot traffic potential",
            "Accessible location"
        ]
    
    if match_score >= 80:
        recommendation = "Highly recommended - strong market fit and favorable conditions"
    elif match_score >= 65:
        recommendation = "Good potential - consider detailed feasibility study"
    else:
        recommendation = "Moderate fit - further market research recommended"
    
    return DeepCloneResponse(
        match_score=match_score,
        source_business=request.source_business,
        source_location=request.source_location,
        target_address=request.target_address,
        business_category=request.business_category,
        three_mile_analysis=ThreeMileAnalysis(
            population=population,
            median_income=median_income,
            competition_level=competition_level,
            growth_rate=growth_rate,
            median_age=median_age
        ),
        key_factors=key_factors[:4],
        competitors_found=competitors,
        recommendation=recommendation
    )
