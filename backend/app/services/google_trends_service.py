"""
Google Trends Service via SerpAPI

Fetches search trend data at DMA (Designated Market Area) level.
Note: Google Trends does NOT support zipcode-level granularity.
Best available: DMA (Metro areas) and City level.

Uses zipcode-to-DMA mapping to translate locations.
"""

import os
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

try:
    from serpapi import GoogleSearch
except ImportError:
    GoogleSearch = None

logger = logging.getLogger(__name__)


# Common US state abbreviations to FIPS codes for DMA mapping
STATE_TO_FIPS = {
    "AL": "01", "AK": "02", "AZ": "04", "AR": "05", "CA": "06",
    "CO": "08", "CT": "09", "DE": "10", "FL": "12", "GA": "13",
    "HI": "15", "ID": "16", "IL": "17", "IN": "18", "IA": "19",
    "KS": "20", "KY": "21", "LA": "22", "ME": "23", "MD": "24",
    "MA": "25", "MI": "26", "MN": "27", "MS": "28", "MO": "29",
    "MT": "30", "NE": "31", "NV": "32", "NH": "33", "NJ": "34",
    "NM": "35", "NY": "36", "NC": "37", "ND": "38", "OH": "39",
    "OK": "40", "OR": "41", "PA": "42", "RI": "44", "SC": "45",
    "SD": "46", "TN": "47", "TX": "48", "UT": "49", "VT": "50",
    "VA": "51", "WA": "53", "WV": "54", "WI": "55", "WY": "56",
    "DC": "11"
}

# Major metro areas and their DMA codes (subset for common cities)
CITY_TO_DMA = {
    "new york": "501",
    "los angeles": "803",
    "chicago": "602",
    "houston": "618",
    "phoenix": "753",
    "philadelphia": "504",
    "san antonio": "641",
    "san diego": "825",
    "dallas": "623",
    "san jose": "807",
    "austin": "635",
    "jacksonville": "561",
    "fort worth": "623",
    "columbus": "535",
    "charlotte": "517",
    "san francisco": "807",
    "indianapolis": "527",
    "seattle": "819",
    "denver": "751",
    "boston": "506",
    "nashville": "659",
    "detroit": "505",
    "portland": "820",
    "las vegas": "839",
    "memphis": "640",
    "louisville": "529",
    "baltimore": "512",
    "milwaukee": "617",
    "albuquerque": "790",
    "tucson": "789",
    "fresno": "866",
    "sacramento": "862",
    "kansas city": "616",
    "atlanta": "524",
    "miami": "528",
    "minneapolis": "613",
    "cleveland": "510",
    "tampa": "539",
    "st. louis": "609",
    "pittsburgh": "508",
    "cincinnati": "515",
    "orlando": "534",
    "raleigh": "560",
    "salt lake city": "770",
}


class GoogleTrendsService:
    def __init__(self):
        self.api_key = os.getenv("SERPAPI_KEY")
    
    @property
    def is_configured(self) -> bool:
        return bool(self.api_key) and GoogleSearch is not None
    
    def get_dma_code(self, city: str = None, state: str = None) -> Optional[str]:
        """
        Get DMA code from city or state.
        
        Args:
            city: City name
            state: State name or abbreviation
        
        Returns:
            DMA code string or None
        """
        if city:
            city_lower = city.lower().strip()
            if city_lower in CITY_TO_DMA:
                return CITY_TO_DMA[city_lower]
        
        # Fall back to state-level trends if no city match
        return None
    
    def get_state_code(self, state: str) -> Optional[str]:
        """Convert state name/abbreviation to geo code for Google Trends."""
        if not state:
            return None
        
        state_upper = state.upper().strip()
        
        # Check if already an abbreviation
        if len(state_upper) == 2 and state_upper in STATE_TO_FIPS:
            return f"US-{state_upper}"
        
        # Common state name mappings
        state_names = {
            "CALIFORNIA": "CA", "TEXAS": "TX", "FLORIDA": "FL", "NEW YORK": "NY",
            "PENNSYLVANIA": "PA", "ILLINOIS": "IL", "OHIO": "OH", "GEORGIA": "GA",
            "NORTH CAROLINA": "NC", "MICHIGAN": "MI", "NEW JERSEY": "NJ",
            "VIRGINIA": "VA", "WASHINGTON": "WA", "ARIZONA": "AZ", "MASSACHUSETTS": "MA",
            "TENNESSEE": "TN", "INDIANA": "IN", "MARYLAND": "MD", "MISSOURI": "MO",
            "WISCONSIN": "WI", "COLORADO": "CO", "MINNESOTA": "MN", "SOUTH CAROLINA": "SC",
            "ALABAMA": "AL", "LOUISIANA": "LA", "KENTUCKY": "KY", "OREGON": "OR",
            "OKLAHOMA": "OK", "CONNECTICUT": "CT", "UTAH": "UT", "IOWA": "IA",
            "NEVADA": "NV", "ARKANSAS": "AR", "MISSISSIPPI": "MS", "KANSAS": "KS",
            "NEW MEXICO": "NM", "NEBRASKA": "NE", "IDAHO": "ID", "WEST VIRGINIA": "WV",
            "HAWAII": "HI", "NEW HAMPSHIRE": "NH", "MAINE": "ME", "MONTANA": "MT",
            "RHODE ISLAND": "RI", "DELAWARE": "DE", "SOUTH DAKOTA": "SD",
            "NORTH DAKOTA": "ND", "ALASKA": "AK", "VERMONT": "VT", "WYOMING": "WY",
            "DISTRICT OF COLUMBIA": "DC"
        }
        
        abbr = state_names.get(state_upper)
        if abbr:
            return f"US-{abbr}"
        
        return None
    
    def fetch_interest_over_time(
        self,
        keyword: str,
        geo: str = "US",
        time_range: str = "today 12-m"
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch Google Trends interest over time data.
        
        Args:
            keyword: Search term to analyze
            geo: Geographic code (US, US-CA, US-CA-803 for DMA)
            time_range: Time range (today 12-m, today 3-m, past 5-y, etc.)
        
        Returns:
            Dictionary with trend data or None
        """
        if not self.is_configured:
            logger.warning("SerpAPI not configured for Google Trends")
            return None
        
        try:
            params = {
                "api_key": self.api_key,
                "engine": "google_trends",
                "q": keyword,
                "geo": geo,
                "date": time_range,
                "data_type": "TIMESERIES"
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            interest_over_time = results.get("interest_over_time", {})
            timeline_data = interest_over_time.get("timeline_data", [])
            
            # Extract key metrics
            if timeline_data:
                values = [d.get("values", [{}])[0].get("extracted_value", 0) for d in timeline_data]
                values = [v for v in values if v is not None]
                
                if values:
                    return {
                        "keyword": keyword,
                        "geo": geo,
                        "time_range": time_range,
                        "average_interest": round(sum(values) / len(values), 1),
                        "peak_interest": max(values),
                        "current_interest": values[-1] if values else 0,
                        "trend_direction": "rising" if len(values) > 1 and values[-1] > values[0] else "declining",
                        "data_points": len(values),
                        "fetched_at": datetime.now().isoformat()
                    }
            
            return {
                "keyword": keyword,
                "geo": geo,
                "time_range": time_range,
                "average_interest": 0,
                "peak_interest": 0,
                "current_interest": 0,
                "trend_direction": "unknown",
                "data_points": 0,
                "fetched_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error fetching Google Trends for '{keyword}': {e}")
            return None
    
    def fetch_related_queries(
        self,
        keyword: str,
        geo: str = "US"
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch related search queries for a keyword.
        
        Args:
            keyword: Search term to analyze
            geo: Geographic code
        
        Returns:
            Dictionary with related queries or None
        """
        if not self.is_configured:
            return None
        
        try:
            params = {
                "api_key": self.api_key,
                "engine": "google_trends",
                "q": keyword,
                "geo": geo,
                "data_type": "RELATED_QUERIES"
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            related = results.get("related_queries", {})
            
            return {
                "keyword": keyword,
                "geo": geo,
                "rising": related.get("rising", [])[:10],
                "top": related.get("top", [])[:10],
                "fetched_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error fetching related queries for '{keyword}': {e}")
            return None
    
    def fetch_interest_by_region(
        self,
        keyword: str,
        geo: str = "US",
        resolution: str = "DMA"
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch search interest by geographic region.
        
        Args:
            keyword: Search term to analyze
            geo: Geographic code
            resolution: COUNTRY, REGION, DMA, or CITY
        
        Returns:
            Dictionary with regional interest data or None
        """
        if not self.is_configured:
            return None
        
        try:
            params = {
                "api_key": self.api_key,
                "engine": "google_trends",
                "q": keyword,
                "geo": geo,
                "data_type": "GEO_MAP",
                "resolution": resolution
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            geo_data = results.get("interest_by_region", [])
            
            return {
                "keyword": keyword,
                "geo": geo,
                "resolution": resolution,
                "regions": geo_data[:20],  # Top 20 regions
                "fetched_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error fetching regional interest for '{keyword}': {e}")
            return None
    
    def analyze_opportunity_demand(
        self,
        opportunity_title: str,
        category: str,
        city: str = None,
        state: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze search demand for an opportunity.
        
        Args:
            opportunity_title: Title of the opportunity
            category: Opportunity category
            city: City name (optional)
            state: State name (optional)
        
        Returns:
            Comprehensive trend analysis or None
        """
        if not self.is_configured:
            return None
        
        # Determine geographic scope
        geo = "US"
        if city:
            dma = self.get_dma_code(city)
            if dma:
                state_code = self.get_state_code(state)
                if state_code:
                    geo = f"{state_code}-{dma}"
        elif state:
            state_geo = self.get_state_code(state)
            if state_geo:
                geo = state_geo
        
        # Extract keywords from title (simple approach)
        keywords = self._extract_keywords(opportunity_title, category)
        
        results = {
            "opportunity_title": opportunity_title,
            "category": category,
            "geo": geo,
            "keywords_analyzed": keywords,
            "keyword_trends": [],
            "overall_demand_score": 0,
            "fetched_at": datetime.now().isoformat()
        }
        
        total_interest = 0
        analyzed_count = 0
        
        for keyword in keywords[:3]:  # Limit to top 3 keywords
            trend = self.fetch_interest_over_time(keyword, geo)
            if trend:
                results["keyword_trends"].append(trend)
                total_interest += trend.get("average_interest", 0)
                analyzed_count += 1
        
        if analyzed_count > 0:
            results["overall_demand_score"] = round(total_interest / analyzed_count, 1)
        
        return results
    
    def _extract_keywords(self, title: str, category: str) -> List[str]:
        """Extract searchable keywords from opportunity title."""
        # Simple keyword extraction - could be enhanced with NLP
        stop_words = {
            "is", "are", "the", "a", "an", "and", "or", "but", "in", "on", "at",
            "to", "for", "of", "with", "by", "from", "as", "into", "through",
            "during", "before", "after", "above", "below", "too", "very", "just",
            "i", "my", "me", "we", "our", "you", "your", "it", "its", "this",
            "that", "these", "those", "have", "has", "had", "do", "does", "did",
            "will", "would", "could", "should", "may", "might", "must", "can",
            "need", "want", "like", "find", "finding", "get", "getting", "make",
            "making", "be", "been", "being", "difficult", "hard", "easy"
        }
        
        # Clean and split title
        words = title.lower().replace("'", "").split()
        words = [w.strip(".,!?") for w in words if len(w) > 2]
        
        # Build keywords
        keywords = []
        
        # Add category as a keyword
        keywords.append(category.lower())
        
        # Add meaningful word combinations
        meaningful_words = [w for w in words if w not in stop_words]
        
        if len(meaningful_words) >= 2:
            keywords.append(" ".join(meaningful_words[:3]))
        
        for word in meaningful_words[:3]:
            if word not in keywords:
                keywords.append(word)
        
        return keywords[:5]


# Singleton instance
google_trends_service = GoogleTrendsService()
