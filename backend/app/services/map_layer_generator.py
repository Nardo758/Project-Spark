"""
Map Layer Generator Service

Generates GeoJSON layers for map visualization including:
- Competition points from SerpAPI data
- Demographics overlays from Census data
- Heatmaps for various metrics
"""

import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class GeoJSONFeature:
    """Single GeoJSON feature"""
    type: str = "Feature"
    geometry: Dict[str, Any] = None
    properties: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "geometry": self.geometry or {},
            "properties": self.properties or {}
        }


@dataclass
class GeoJSONFeatureCollection:
    """GeoJSON FeatureCollection"""
    type: str = "FeatureCollection"
    features: List[GeoJSONFeature] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "features": [f.to_dict() for f in (self.features or [])]
        }


class MapLayerGenerator:
    """Generates GeoJSON layers for map visualization"""
    
    def __init__(self):
        self._serpapi_service = None
        self._census_service = None
    
    @property
    def serpapi_service(self):
        if self._serpapi_service is None:
            try:
                from app.services.serpapi_service import serpapi_service
                self._serpapi_service = serpapi_service
            except ImportError:
                logger.warning("SerpAPI service not available")
        return self._serpapi_service
    
    @property
    def census_service(self):
        if self._census_service is None:
            try:
                from app.services.census_service import census_service
                self._census_service = census_service
            except ImportError:
                logger.warning("Census service not available")
        return self._census_service
    
    async def generate_competition_layer(
        self,
        business_type: str,
        latitude: float,
        longitude: float,
        radius_miles: float = 10.0,
        limit: int = 50
    ) -> Dict[str, Any]:
        """Generate a GeoJSON layer of competitor locations"""
        
        features = []
        
        if self.serpapi_service:
            try:
                query = f"{business_type} near {latitude},{longitude}"
                results = await self.serpapi_service.search_local_businesses(
                    query=query,
                    lat=latitude,
                    lng=longitude,
                    radius_meters=int(radius_miles * 1609.34)
                )
                
                for idx, business in enumerate(results.get("local_results", [])[:limit]):
                    gps = business.get("gps_coordinates", {})
                    if gps.get("latitude") and gps.get("longitude"):
                        feature = GeoJSONFeature(
                            geometry={
                                "type": "Point",
                                "coordinates": [gps["longitude"], gps["latitude"]]
                            },
                            properties={
                                "id": f"comp_{idx}",
                                "name": business.get("title", "Unknown"),
                                "address": business.get("address", ""),
                                "rating": business.get("rating"),
                                "reviews": business.get("reviews"),
                                "type": business.get("type", business_type),
                                "phone": business.get("phone"),
                                "website": business.get("website"),
                                "hours": business.get("hours"),
                                "layer_type": "competition"
                            }
                        )
                        features.append(feature)
                        
            except Exception as e:
                logger.error(f"Failed to fetch competition data: {e}")
        
        collection = GeoJSONFeatureCollection(features=features)
        
        return {
            "layer_id": "competition",
            "layer_type": "points",
            "geojson": collection.to_dict(),
            "metadata": {
                "business_type": business_type,
                "center": [longitude, latitude],
                "radius_miles": radius_miles,
                "count": len(features),
                "generated_at": datetime.utcnow().isoformat()
            }
        }
    
    async def generate_demographics_layer(
        self,
        state_fips: str,
        metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate demographics data for a state"""
        
        if not metrics:
            metrics = ["population", "median_income", "median_age"]
        
        demographics = {}
        
        if self.census_service:
            try:
                data = await self.census_service.get_state_demographics(state_fips)
                demographics = data
            except Exception as e:
                logger.error(f"Failed to fetch census data: {e}")
        
        return {
            "layer_id": "demographics",
            "layer_type": "data",
            "data": demographics,
            "metadata": {
                "state_fips": state_fips,
                "metrics": metrics,
                "generated_at": datetime.utcnow().isoformat()
            }
        }
    
    def generate_heatmap_layer(
        self,
        points: List[Dict[str, Any]],
        metric: str = "density",
        radius: int = 30,
        intensity: float = 1.0
    ) -> Dict[str, Any]:
        """Generate a heatmap layer from point data"""
        
        features = []
        
        for idx, point in enumerate(points):
            if "latitude" in point and "longitude" in point:
                weight = point.get("weight", point.get(metric, 1.0))
                feature = GeoJSONFeature(
                    geometry={
                        "type": "Point",
                        "coordinates": [point["longitude"], point["latitude"]]
                    },
                    properties={
                        "id": f"heat_{idx}",
                        "weight": weight,
                        "metric": metric
                    }
                )
                features.append(feature)
        
        collection = GeoJSONFeatureCollection(features=features)
        
        return {
            "layer_id": f"heatmap_{metric}",
            "layer_type": "heatmap",
            "geojson": collection.to_dict(),
            "config": {
                "radius": radius,
                "intensity": intensity,
                "metric": metric
            },
            "metadata": {
                "point_count": len(features),
                "generated_at": datetime.utcnow().isoformat()
            }
        }
    
    def generate_comparison_layer(
        self,
        locations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate a comparison layer with multiple location markers"""
        
        features = []
        
        for idx, loc in enumerate(locations):
            if "latitude" in loc and "longitude" in loc:
                feature = GeoJSONFeature(
                    geometry={
                        "type": "Point",
                        "coordinates": [loc["longitude"], loc["latitude"]]
                    },
                    properties={
                        "id": f"compare_{idx}",
                        "name": loc.get("name", f"Location {idx + 1}"),
                        "score": loc.get("score"),
                        "metrics": loc.get("metrics", {}),
                        "rank": idx + 1,
                        "layer_type": "comparison"
                    }
                )
                features.append(feature)
        
        collection = GeoJSONFeatureCollection(features=features)
        
        return {
            "layer_id": "comparison",
            "layer_type": "comparison_points",
            "geojson": collection.to_dict(),
            "metadata": {
                "location_count": len(features),
                "generated_at": datetime.utcnow().isoformat()
            }
        }
    
    def generate_radius_circle(
        self,
        center_lat: float,
        center_lng: float,
        radius_miles: float,
        num_points: int = 64
    ) -> Dict[str, Any]:
        """Generate a circle polygon for radius visualization"""
        import math
        
        radius_km = radius_miles * 1.60934
        coordinates = []
        
        for i in range(num_points + 1):
            angle = (2 * math.pi * i) / num_points
            dx = radius_km * math.cos(angle)
            dy = radius_km * math.sin(angle)
            
            lat = center_lat + (dy / 111.32)
            lng = center_lng + (dx / (111.32 * math.cos(math.radians(center_lat))))
            coordinates.append([lng, lat])
        
        feature = GeoJSONFeature(
            geometry={
                "type": "Polygon",
                "coordinates": [coordinates]
            },
            properties={
                "id": "radius_circle",
                "radius_miles": radius_miles,
                "center": [center_lng, center_lat],
                "layer_type": "radius"
            }
        )
        
        collection = GeoJSONFeatureCollection(features=[feature])
        
        return {
            "layer_id": "radius",
            "layer_type": "polygon",
            "geojson": collection.to_dict(),
            "metadata": {
                "center": [center_lng, center_lat],
                "radius_miles": radius_miles,
                "generated_at": datetime.utcnow().isoformat()
            }
        }


map_layer_generator = MapLayerGenerator()
