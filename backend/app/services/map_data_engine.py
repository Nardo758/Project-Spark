import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.geographic_feature import GeographicFeature, FeatureType
from app.models.map_layer import MapLayer, LayerType
from app.models.user_map_session import UserMapSession
from app.models.location_analysis_cache import LocationAnalysisCache

logger = logging.getLogger(__name__)


class MapDataEngine:
    """
    Map Data Engine Service
    Manages map layers and serves mapData to frontend for Leaflet.js rendering.
    """

    DEFAULT_LAYERS = [
        {
            "layer_name": "business_pins",
            "layer_type": LayerType.pins.value,
            "data_source": "google_maps,yelp",
            "description": "Business locations from Google Maps and Yelp",
            "style_spec": {
                "icon": "business",
                "color": "#4285F4",
                "size": 24,
            },
            "display_order": 1,
        },
        {
            "layer_name": "problem_heatmap",
            "layer_type": LayerType.heatmap.value,
            "data_source": "reddit,twitter",
            "description": "Problem intensity heatmap from social media",
            "style_spec": {
                "gradient": {"0.4": "blue", "0.6": "yellow", "1": "red"},
                "radius": 25,
                "blur": 15,
                "maxZoom": 17,
            },
            "display_order": 2,
        },
        {
            "layer_name": "neighborhood_polygons",
            "layer_type": LayerType.polygon.value,
            "data_source": "nextdoor",
            "description": "Neighborhood boundaries from Nextdoor",
            "style_spec": {
                "fillColor": "#9C27B0",
                "fillOpacity": 0.2,
                "color": "#7B1FA2",
                "weight": 2,
            },
            "display_order": 3,
        },
    ]

    def __init__(self, db: Session):
        self.db = db

    def initialize_default_layers(self) -> List[MapLayer]:
        """Create default map layers if they don't exist"""
        created = []
        for layer_config in self.DEFAULT_LAYERS:
            existing = self.db.query(MapLayer).filter(
                MapLayer.layer_name == layer_config["layer_name"]
            ).first()
            
            if not existing:
                layer = MapLayer(**layer_config)
                self.db.add(layer)
                created.append(layer)
        
        if created:
            self.db.commit()
        return created

    def get_all_layers(self) -> List[Dict[str, Any]]:
        """Get all available map layers"""
        layers = self.db.query(MapLayer).order_by(MapLayer.display_order).all()
        return [
            {
                "id": layer.id,
                "name": layer.layer_name,
                "type": layer.layer_type,
                "dataSource": layer.data_source,
                "description": layer.description,
                "style": layer.style_spec,
                "enabled": layer.enabled,
            }
            for layer in layers
        ]

    def get_map_data_for_bounds(
        self,
        bounds: Dict[str, float],
        layers: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Get map data for a given geographic bounds.
        
        Args:
            bounds: {north, south, east, west} lat/lng bounds
            layers: List of layer names to include (None = all)
            filters: Additional filters to apply
        
        Returns:
            MapData structure for frontend rendering
        """
        north = bounds.get("north", 90)
        south = bounds.get("south", -90)
        east = bounds.get("east", 180)
        west = bounds.get("west", -180)

        query = self.db.query(GeographicFeature).filter(
            and_(
                GeographicFeature.latitude.isnot(None),
                GeographicFeature.longitude.isnot(None),
                GeographicFeature.latitude <= north,
                GeographicFeature.latitude >= south,
                GeographicFeature.longitude <= east,
                GeographicFeature.longitude >= west,
            )
        )

        if filters:
            if filters.get("city"):
                query = query.filter(GeographicFeature.city.ilike(f"%{filters['city']}%"))
            if filters.get("source"):
                sources = filters["source"].split(",")
                query = query.join(GeographicFeature.source_id).filter(
                    GeographicFeature.source_id.in_(sources)
                )

        features = query.limit(5000).all()

        pins = []
        heatmap_points = []
        polygons = []

        for feature in features:
            props = feature.properties or {}
            source = props.get("source", "")

            if feature.feature_type == FeatureType.polygon.value:
                polygons.append(feature.geojson)
            elif source in ["google_maps", "yelp"]:
                pins.append({
                    "id": feature.id,
                    "lat": feature.latitude,
                    "lng": feature.longitude,
                    "name": props.get("name", ""),
                    "rating": props.get("rating"),
                    "reviews": props.get("reviews_count"),
                    "source": source,
                    "popup": self._build_popup_content(feature),
                })
            elif source in ["reddit", "twitter"]:
                heatmap_points.append({
                    "lat": feature.latitude,
                    "lng": feature.longitude,
                    "intensity": props.get("intensity", 0.5),
                    "title": props.get("title", ""),
                    "source": source,
                })
            else:
                pins.append({
                    "id": feature.id,
                    "lat": feature.latitude,
                    "lng": feature.longitude,
                    "name": props.get("name") or feature.location_name or "Unknown",
                    "source": source,
                    "popup": self._build_popup_content(feature),
                })

        return {
            "bounds": bounds,
            "layers": {
                "pins": {
                    "type": "pins",
                    "data": pins,
                    "count": len(pins),
                },
                "heatmap": {
                    "type": "heatmap",
                    "data": heatmap_points,
                    "count": len(heatmap_points),
                },
                "polygons": {
                    "type": "polygons",
                    "data": polygons,
                    "count": len(polygons),
                },
            },
            "totalFeatures": len(features),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def get_map_data_for_city(
        self,
        city: str,
        state: Optional[str] = None,
        layers: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Get map data for a specific city"""
        query = self.db.query(GeographicFeature).filter(
            GeographicFeature.city.ilike(f"%{city}%")
        )
        
        if state:
            query = query.filter(GeographicFeature.state.ilike(f"%{state}%"))

        features = query.limit(2000).all()

        if not features:
            return {
                "city": city,
                "state": state,
                "layers": {"pins": {"data": [], "count": 0}, "heatmap": {"data": [], "count": 0}, "polygons": {"data": [], "count": 0}},
                "totalFeatures": 0,
                "bounds": None,
            }

        lats = [f.latitude for f in features if f.latitude]
        lngs = [f.longitude for f in features if f.longitude]
        
        bounds = {
            "north": max(lats) if lats else 0,
            "south": min(lats) if lats else 0,
            "east": max(lngs) if lngs else 0,
            "west": min(lngs) if lngs else 0,
        }

        pins = []
        heatmap_points = []
        polygons = []

        for feature in features:
            props = feature.properties or {}
            source = props.get("source", "")

            if feature.feature_type == FeatureType.polygon.value:
                polygons.append(feature.geojson)
            elif source in ["google_maps", "yelp"]:
                if feature.latitude and feature.longitude:
                    pins.append({
                        "id": feature.id,
                        "lat": feature.latitude,
                        "lng": feature.longitude,
                        "name": props.get("name", ""),
                        "rating": props.get("rating"),
                        "reviews": props.get("reviews_count"),
                        "source": source,
                        "popup": self._build_popup_content(feature),
                    })
            elif source in ["reddit", "twitter"]:
                if feature.latitude and feature.longitude:
                    heatmap_points.append({
                        "lat": feature.latitude,
                        "lng": feature.longitude,
                        "intensity": props.get("intensity", 0.5),
                        "title": props.get("title", ""),
                        "source": source,
                    })

        return {
            "city": city,
            "state": state,
            "bounds": bounds,
            "center": {
                "lat": (bounds["north"] + bounds["south"]) / 2,
                "lng": (bounds["east"] + bounds["west"]) / 2,
            },
            "layers": {
                "pins": {"type": "pins", "data": pins, "count": len(pins)},
                "heatmap": {"type": "heatmap", "data": heatmap_points, "count": len(heatmap_points)},
                "polygons": {"type": "polygons", "data": polygons, "count": len(polygons)},
            },
            "totalFeatures": len(features),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _build_popup_content(self, feature: GeographicFeature) -> str:
        """Build HTML popup content for a map marker"""
        props = feature.properties or {}
        name = props.get("name") or feature.location_name or "Unknown"
        source = props.get("source", "")
        
        html = f"<div class='map-popup'><strong>{name}</strong>"
        
        if props.get("rating"):
            html += f"<br/>Rating: {props['rating']} stars"
        if props.get("reviews_count"):
            html += f" ({props['reviews_count']} reviews)"
        if props.get("address"):
            html += f"<br/>{props['address']}"
        if props.get("categories"):
            html += f"<br/>Categories: {', '.join(props['categories'][:3])}"
        
        html += f"<br/><small>Source: {source}</small></div>"
        return html

    def save_user_session(
        self,
        user_id: int,
        layer_state: Dict[str, bool],
        viewport: Dict[str, Any],
        session_name: Optional[str] = None,
    ) -> UserMapSession:
        """Save user's map session state"""
        session = UserMapSession(
            user_id=user_id,
            session_name=session_name,
            layer_state=layer_state,
            viewport=viewport,
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_user_sessions(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user's recent map sessions"""
        sessions = self.db.query(UserMapSession).filter(
            UserMapSession.user_id == user_id
        ).order_by(UserMapSession.created_at.desc()).limit(limit).all()
        
        return [
            {
                "id": s.id,
                "name": s.session_name,
                "layerState": s.layer_state,
                "viewport": s.viewport,
                "createdAt": s.created_at.isoformat() if s.created_at else None,
            }
            for s in sessions
        ]

    def get_layer_statistics(self) -> Dict[str, Any]:
        """Get statistics about geographic features by layer"""
        from sqlalchemy import func
        
        stats = {}
        
        total = self.db.query(func.count(GeographicFeature.id)).scalar()
        stats["total_features"] = total
        
        by_type = self.db.query(
            GeographicFeature.feature_type,
            func.count(GeographicFeature.id)
        ).group_by(GeographicFeature.feature_type).all()
        
        stats["by_type"] = {t: c for t, c in by_type}
        
        cities = self.db.query(
            GeographicFeature.city,
            func.count(GeographicFeature.id)
        ).filter(
            GeographicFeature.city.isnot(None)
        ).group_by(GeographicFeature.city).order_by(
            func.count(GeographicFeature.id).desc()
        ).limit(10).all()
        
        stats["top_cities"] = [{"city": c, "count": n} for c, n in cities]
        
        return stats
