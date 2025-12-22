import logging
import re
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session

from app.models.scraped_source import ScrapedSource, SourceType
from app.models.geographic_feature import GeographicFeature, FeatureType

logger = logging.getLogger(__name__)


class GeographicExtractor:
    """
    Geographic Extractor Service
    Converts location data from various sources into standardized GeoJSON format.
    """

    def __init__(self, db: Session):
        self.db = db

    def extract_from_source(self, source: ScrapedSource) -> Optional[GeographicFeature]:
        """Extract geographic features from a scraped source"""
        extractors = {
            SourceType.google_maps.value: self._extract_google_maps,
            SourceType.yelp.value: self._extract_yelp,
            SourceType.reddit.value: self._extract_reddit,
            SourceType.twitter.value: self._extract_twitter,
            SourceType.nextdoor.value: self._extract_nextdoor,
            SourceType.custom.value: self._extract_custom,
        }

        extractor = extractors.get(source.source_type)
        if not extractor:
            logger.warning(f"No extractor for source type: {source.source_type}")
            return None

        return extractor(source)

    def _extract_google_maps(self, source: ScrapedSource) -> Optional[GeographicFeature]:
        """Extract location from Google Maps data"""
        data = source.raw_data
        location = data.get("location", {}) or data.get("geometry", {}).get("location", {})
        
        lat = location.get("lat") or location.get("latitude")
        lng = location.get("lng") or location.get("longitude")

        if lat is None or lng is None:
            return None

        geojson = self._create_point_geojson(
            lat=float(lat),
            lng=float(lng),
            properties={
                "name": data.get("name", ""),
                "rating": data.get("rating"),
                "reviews_count": data.get("user_ratings_total") or data.get("reviews_count"),
                "place_id": data.get("place_id"),
                "types": data.get("types", []),
                "address": data.get("formatted_address") or data.get("address"),
                "source": "google_maps",
            }
        )

        return GeographicFeature(
            source_id=source.id,
            latitude=float(lat),
            longitude=float(lng),
            geojson=geojson,
            feature_type=FeatureType.point.value,
            location_name=data.get("name"),
            city=self._extract_city(data.get("formatted_address", "")),
            properties=geojson["properties"],
            confidence_score=0.95,
        )

    def _extract_yelp(self, source: ScrapedSource) -> Optional[GeographicFeature]:
        """Extract location from Yelp data"""
        data = source.raw_data
        coords = data.get("coordinates", {})
        
        lat = coords.get("latitude")
        lng = coords.get("longitude")

        if lat is None or lng is None:
            location = data.get("location", {})
            return None

        geojson = self._create_point_geojson(
            lat=float(lat),
            lng=float(lng),
            properties={
                "name": data.get("name", ""),
                "rating": data.get("rating"),
                "reviews_count": data.get("review_count"),
                "business_id": data.get("business_id") or data.get("id"),
                "categories": [c.get("title") for c in data.get("categories", [])],
                "price": data.get("price"),
                "source": "yelp",
            }
        )

        location = data.get("location", {})
        return GeographicFeature(
            source_id=source.id,
            latitude=float(lat),
            longitude=float(lng),
            geojson=geojson,
            feature_type=FeatureType.point.value,
            location_name=data.get("name"),
            city=location.get("city"),
            state=location.get("state"),
            country=location.get("country"),
            postal_code=location.get("zip_code"),
            properties=geojson["properties"],
            confidence_score=0.95,
        )

    def _extract_reddit(self, source: ScrapedSource) -> Optional[GeographicFeature]:
        """Extract location hints from Reddit posts"""
        data = source.raw_data
        
        text = f"{data.get('title', '')} {data.get('selftext', '')} {data.get('body', '')}"
        
        location = self._extract_location_from_text(text)
        if not location:
            subreddit = data.get("subreddit", "")
            location = self._infer_location_from_subreddit(subreddit)

        if not location or not location.get("lat"):
            geojson = {
                "type": "Feature",
                "geometry": None,
                "properties": {
                    "post_id": data.get("post_id") or data.get("id"),
                    "subreddit": data.get("subreddit"),
                    "title": data.get("title"),
                    "sentiment": data.get("sentiment"),
                    "intensity": self._calculate_intensity(data),
                    "location_hint": location.get("hint") if location else None,
                    "source": "reddit",
                }
            }
            return GeographicFeature(
                source_id=source.id,
                geojson=geojson,
                feature_type=FeatureType.point.value,
                city=location.get("city") if location else None,
                properties=geojson["properties"],
                confidence_score=0.3,
            )

        lat, lng = location["lat"], location["lng"]
        geojson = self._create_point_geojson(
            lat=lat,
            lng=lng,
            properties={
                "post_id": data.get("post_id") or data.get("id"),
                "subreddit": data.get("subreddit"),
                "title": data.get("title"),
                "sentiment": data.get("sentiment"),
                "intensity": self._calculate_intensity(data),
                "source": "reddit",
            }
        )

        return GeographicFeature(
            source_id=source.id,
            latitude=lat,
            longitude=lng,
            geojson=geojson,
            feature_type=FeatureType.point.value,
            city=location.get("city"),
            properties=geojson["properties"],
            confidence_score=location.get("confidence", 0.5),
        )

    def _extract_twitter(self, source: ScrapedSource) -> Optional[GeographicFeature]:
        """Extract location from Twitter data"""
        data = source.raw_data
        
        geo = data.get("geo", {})
        coords = geo.get("coordinates", {}).get("coordinates", [])
        
        if len(coords) >= 2:
            lng, lat = coords[0], coords[1]
        else:
            place = data.get("place", {})
            bbox = place.get("bounding_box", {}).get("coordinates", [[]])[0]
            if bbox:
                lat = sum(c[1] for c in bbox) / len(bbox)
                lng = sum(c[0] for c in bbox) / len(bbox)
            else:
                return None

        geojson = self._create_point_geojson(
            lat=float(lat),
            lng=float(lng),
            properties={
                "tweet_id": data.get("tweet_id") or data.get("id"),
                "text": data.get("text"),
                "sentiment": data.get("sentiment"),
                "intensity": self._calculate_intensity(data),
                "source": "twitter",
            }
        )

        return GeographicFeature(
            source_id=source.id,
            latitude=float(lat),
            longitude=float(lng),
            geojson=geojson,
            feature_type=FeatureType.point.value,
            properties=geojson["properties"],
            confidence_score=0.85,
        )

    def _extract_nextdoor(self, source: ScrapedSource) -> Optional[GeographicFeature]:
        """Extract neighborhood polygon from Nextdoor data"""
        data = source.raw_data
        
        boundary = data.get("neighborhood_boundary") or data.get("boundary")
        if boundary and isinstance(boundary, dict):
            geojson = {
                "type": "Feature",
                "geometry": boundary,
                "properties": {
                    "neighborhood": data.get("neighborhood"),
                    "post_density": data.get("post_density", 0),
                    "activity_score": data.get("activity_score", 0),
                    "source": "nextdoor",
                }
            }
            feature_type = FeatureType.polygon.value
            lat, lng = self._get_polygon_center(boundary)
        else:
            lat = data.get("latitude") or data.get("lat")
            lng = data.get("longitude") or data.get("lng")
            if lat is None or lng is None:
                return None
            
            geojson = self._create_point_geojson(
                lat=float(lat),
                lng=float(lng),
                properties={
                    "neighborhood": data.get("neighborhood"),
                    "post_density": data.get("post_density", 0),
                    "source": "nextdoor",
                }
            )
            feature_type = FeatureType.point.value

        return GeographicFeature(
            source_id=source.id,
            latitude=float(lat) if lat else None,
            longitude=float(lng) if lng else None,
            geojson=geojson,
            feature_type=feature_type,
            location_name=data.get("neighborhood"),
            properties=geojson["properties"],
            confidence_score=0.8,
        )

    def _extract_custom(self, source: ScrapedSource) -> Optional[GeographicFeature]:
        """Extract location from custom source data"""
        data = source.raw_data
        
        lat = data.get("latitude") or data.get("lat")
        lng = data.get("longitude") or data.get("lng") or data.get("lon")

        if lat is None or lng is None:
            return None

        geojson = self._create_point_geojson(
            lat=float(lat),
            lng=float(lng),
            properties={
                "id": data.get("id"),
                "data": data.get("data"),
                "source": "custom",
            }
        )

        return GeographicFeature(
            source_id=source.id,
            latitude=float(lat),
            longitude=float(lng),
            geojson=geojson,
            feature_type=FeatureType.point.value,
            city=data.get("city"),
            properties=geojson["properties"],
            confidence_score=0.7,
        )

    def _create_point_geojson(
        self, 
        lat: float, 
        lng: float, 
        properties: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a GeoJSON Point feature"""
        return {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lng, lat]
            },
            "properties": properties
        }

    def _extract_city(self, address: str) -> Optional[str]:
        """Extract city from formatted address"""
        if not address:
            return None
        parts = address.split(",")
        if len(parts) >= 2:
            return parts[-3].strip() if len(parts) >= 3 else parts[0].strip()
        return None

    def _extract_location_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract location hints from text using patterns"""
        city_patterns = [
            r"in ([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
            r"from ([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
            r"near ([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
        ]
        for pattern in city_patterns:
            match = re.search(pattern, text)
            if match:
                return {"hint": match.group(1), "city": match.group(1)}
        return None

    def _infer_location_from_subreddit(self, subreddit: str) -> Optional[Dict[str, Any]]:
        """Infer location from subreddit name"""
        city_subreddits = {
            "nyc": {"city": "New York", "lat": 40.7128, "lng": -74.0060, "confidence": 0.7},
            "losangeles": {"city": "Los Angeles", "lat": 34.0522, "lng": -118.2437, "confidence": 0.7},
            "chicago": {"city": "Chicago", "lat": 41.8781, "lng": -87.6298, "confidence": 0.7},
            "miami": {"city": "Miami", "lat": 25.7617, "lng": -80.1918, "confidence": 0.7},
            "seattle": {"city": "Seattle", "lat": 47.6062, "lng": -122.3321, "confidence": 0.7},
            "sanfrancisco": {"city": "San Francisco", "lat": 37.7749, "lng": -122.4194, "confidence": 0.7},
            "austin": {"city": "Austin", "lat": 30.2672, "lng": -97.7431, "confidence": 0.7},
            "denver": {"city": "Denver", "lat": 39.7392, "lng": -104.9903, "confidence": 0.7},
            "boston": {"city": "Boston", "lat": 42.3601, "lng": -71.0589, "confidence": 0.7},
            "portland": {"city": "Portland", "lat": 45.5051, "lng": -122.6750, "confidence": 0.7},
        }
        return city_subreddits.get(subreddit.lower())

    def _calculate_intensity(self, data: Dict[str, Any]) -> float:
        """Calculate intensity score for heatmap"""
        score = data.get("score", 0) or 0
        comments = data.get("num_comments", 0) or data.get("comments_count", 0) or 0
        intensity = min((score + comments * 2) / 100, 1.0)
        return max(0.1, intensity)

    def _get_polygon_center(self, geometry: Dict[str, Any]) -> Tuple[float, float]:
        """Get the center point of a polygon"""
        coords = geometry.get("coordinates", [[]])
        if geometry.get("type") == "Polygon" and coords:
            ring = coords[0]
            if ring:
                lat = sum(c[1] for c in ring) / len(ring)
                lng = sum(c[0] for c in ring) / len(ring)
                return lat, lng
        return 0.0, 0.0

    async def process_pending_sources(self, limit: int = 50) -> Dict[str, int]:
        """Process all pending scraped sources"""
        from app.services.webhook_gateway import WebhookGateway
        
        gateway = WebhookGateway(self.db)
        sources = gateway.get_unprocessed_sources(limit)
        
        results = {"processed": 0, "features_created": 0, "errors": 0}
        
        for source in sources:
            try:
                feature = self.extract_from_source(source)
                if feature:
                    self.db.add(feature)
                    results["features_created"] += 1
                gateway.mark_processed(source.id)
                results["processed"] += 1
            except Exception as e:
                logger.error(f"Error processing source {source.id}: {e}")
                gateway.mark_processed(source.id, error=str(e))
                results["errors"] += 1
        
        self.db.commit()
        return results
