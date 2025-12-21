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

