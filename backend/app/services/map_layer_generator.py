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


STATE_CENTERS = {
    "01": {"lat": 32.806671, "lng": -86.791130},
    "02": {"lat": 61.370716, "lng": -152.404419},
    "04": {"lat": 33.729759, "lng": -111.431221},
    "05": {"lat": 34.969704, "lng": -92.373123},
    "06": {"lat": 36.116203, "lng": -119.681564},
    "08": {"lat": 39.059811, "lng": -105.311104},
    "09": {"lat": 41.597782, "lng": -72.755371},
    "10": {"lat": 39.318523, "lng": -75.507141},
    "12": {"lat": 27.766279, "lng": -81.686783},
    "13": {"lat": 33.040619, "lng": -83.643074},
    "15": {"lat": 21.094318, "lng": -157.498337},
    "16": {"lat": 44.240459, "lng": -114.478828},
    "17": {"lat": 40.349457, "lng": -88.986137},
    "18": {"lat": 39.849426, "lng": -86.258278},
    "19": {"lat": 42.011539, "lng": -93.210526},
    "20": {"lat": 38.526600, "lng": -96.726486},
    "21": {"lat": 37.668140, "lng": -84.670067},
    "22": {"lat": 31.169546, "lng": -91.867805},
    "23": {"lat": 44.693947, "lng": -69.381927},
    "24": {"lat": 39.063946, "lng": -76.802101},
    "25": {"lat": 42.230171, "lng": -71.530106},
    "26": {"lat": 43.326618, "lng": -84.536095},
    "27": {"lat": 45.694454, "lng": -93.900192},
    "28": {"lat": 32.741646, "lng": -89.678696},
    "29": {"lat": 38.456085, "lng": -92.288368},
    "30": {"lat": 46.921925, "lng": -110.454353},
    "31": {"lat": 41.125370, "lng": -98.268082},
    "32": {"lat": 38.313515, "lng": -117.055374},
    "33": {"lat": 43.452492, "lng": -71.563896},
    "34": {"lat": 40.298904, "lng": -74.521011},
    "35": {"lat": 34.840515, "lng": -106.248482},
    "36": {"lat": 42.165726, "lng": -74.948051},
    "37": {"lat": 35.630066, "lng": -79.806419},
    "38": {"lat": 47.528912, "lng": -99.784012},
    "39": {"lat": 40.388783, "lng": -82.764915},
    "40": {"lat": 35.565342, "lng": -96.928917},
    "41": {"lat": 44.572021, "lng": -122.070938},
    "42": {"lat": 40.590752, "lng": -77.209755},
    "44": {"lat": 41.680893, "lng": -71.511780},
    "45": {"lat": 33.856892, "lng": -80.945007},
    "46": {"lat": 44.299782, "lng": -99.438828},
    "47": {"lat": 35.747845, "lng": -86.692345},
    "48": {"lat": 31.054487, "lng": -97.563461},
    "49": {"lat": 40.150032, "lng": -111.862434},
    "50": {"lat": 44.045876, "lng": -72.710686},
    "51": {"lat": 37.769337, "lng": -78.169968},
    "53": {"lat": 47.400902, "lng": -121.490494},
    "54": {"lat": 38.491226, "lng": -80.954456},
    "55": {"lat": 44.268543, "lng": -89.616508},
    "56": {"lat": 42.755966, "lng": -107.302490},
}


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
        """Generate demographics data for a state as GeoJSON"""
        
        if not metrics:
            metrics = ["population", "median_income", "median_age"]
        
        demographics = {}
        
        if self.census_service:
            try:
                data = await self.census_service.get_state_demographics(state_fips)
                demographics = data
            except Exception as e:
                logger.error(f"Failed to fetch census data: {e}")
        
        state_center = STATE_CENTERS.get(state_fips, {"lat": 39.8283, "lng": -98.5795})
        
        feature = GeoJSONFeature(
            geometry={
                "type": "Point",
                "coordinates": [state_center["lng"], state_center["lat"]]
            },
            properties={
                "id": f"demo_{state_fips}",
                "state_fips": state_fips,
                "layer_type": "demographics",
                **demographics
            }
        )
        
        collection = GeoJSONFeatureCollection(features=[feature])
        
        return {
            "layer_id": "demographics",
            "layer_type": "demographics",
            "geojson": collection.to_dict(),
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
