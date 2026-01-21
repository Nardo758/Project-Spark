"""
MapCommandParser - LLM-powered Natural Language to Structured Map Commands

Parses user natural language requests into structured commands for map operations
like showing competition, demographics, heatmaps, and location comparisons.
"""

import json
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class MapCommandType(str, Enum):
    SHOW_COMPETITION = "show_competition"
    SHOW_DEMOGRAPHICS = "show_demographics"
    SHOW_HEATMAP = "show_heatmap"
    COMPARE_LOCATIONS = "compare_locations"
    ZOOM_TO = "zoom_to"
    CLEAR_LAYER = "clear_layer"
    SET_RADIUS = "set_radius"
    FILTER_BY = "filter_by"
    ANALYZE_AREA = "analyze_area"
    UNKNOWN = "unknown"


@dataclass
class MapCommand:
    command_type: MapCommandType
    location: Optional[str] = None
    locations: Optional[List[str]] = None
    radius_miles: Optional[float] = None
    business_type: Optional[str] = None
    layer_name: Optional[str] = None
    demographic_metrics: Optional[List[str]] = None
    filters: Optional[Dict[str, Any]] = None
    heatmap_metric: Optional[str] = None
    zoom_level: Optional[int] = None
    filter_type: Optional[str] = None
    filter_value: Optional[Any] = None
    raw_query: str = ""
    confidence: float = 0.0
    explanation: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result["command_type"] = self.command_type.value
        return result


COMMAND_PARSER_PROMPT = """You are a map command parser for a business opportunity analysis tool. 
Parse the user's natural language request into a structured command.

Available command types:
- show_competition: Display competitor businesses on the map
- show_demographics: Show demographic data (population, income, age distribution, etc.)
- show_heatmap: Generate a heatmap for specific metrics (foot traffic, demand, etc.)
- compare_locations: Compare multiple cities or areas side by side
- zoom_to: Navigate to a specific location
- clear_layer: Remove a layer from the map
- set_radius: Change the analysis radius
- filter_by: Apply filters to existing data
- analyze_area: Perform detailed analysis of an area
- unknown: Cannot understand the request

For demographics, available metrics include:
- population, median_income, median_age, households, poverty_rate, 
- education_bachelors, education_graduate, unemployment_rate

Respond with a JSON object containing:
{
  "command_type": "one of the types above",
  "location": "primary location if specified",
  "locations": ["list", "of", "locations"] (for compare_locations),
  "radius_miles": number or null,
  "business_type": "type of business being analyzed",
  "layer_name": "layer to clear or modify",
  "demographic_metrics": ["list", "of", "metrics"],
  "filters": {"key": "value"} or null,
  "confidence": 0.0-1.0 how confident you are in the parsing,
  "explanation": "brief explanation of what the command will do"
}

User's opportunity context:
Business Type: {business_type}
Current Location: {current_location}

Parse this request: {user_query}"""


class MapCommandParser:
    """Parses natural language into structured map commands using LLM"""
    
    def __init__(self):
        self._ai_service = None
    
    @property
    def ai_service(self):
        if self._ai_service is None:
            from app.services.ai_provider_service import ai_provider_service
            self._ai_service = ai_provider_service
        return self._ai_service
    
    async def parse(
        self,
        user_query: str,
        user_id: int,
        business_type: Optional[str] = None,
        current_location: Optional[str] = None
    ) -> MapCommand:
        """Parse a natural language query into a structured MapCommand"""
        
        prompt = COMMAND_PARSER_PROMPT.format(
            business_type=business_type or "Not specified",
            current_location=current_location or "Not specified",
            user_query=user_query
        )
        
        try:
            response = await self.ai_service.chat_json(
                user_id=user_id,
                messages=[{"role": "user", "content": prompt}],
                schema={
                    "type": "object",
                    "properties": {
                        "command_type": {"type": "string"},
                        "location": {"type": ["string", "null"]},
                        "locations": {"type": ["array", "null"], "items": {"type": "string"}},
                        "radius_miles": {"type": ["number", "null"]},
                        "business_type": {"type": ["string", "null"]},
                        "layer_name": {"type": ["string", "null"]},
                        "demographic_metrics": {"type": ["array", "null"], "items": {"type": "string"}},
                        "filters": {"type": ["object", "null"]},
                        "confidence": {"type": "number"},
                        "explanation": {"type": "string"}
                    },
                    "required": ["command_type", "confidence", "explanation"]
                }
            )
            
            command_type_str = response.get("command_type", "unknown")
            try:
                command_type = MapCommandType(command_type_str)
            except ValueError:
                command_type = MapCommandType.UNKNOWN
            
            return MapCommand(
                command_type=command_type,
                location=response.get("location"),
                locations=response.get("locations"),
                radius_miles=response.get("radius_miles"),
                business_type=response.get("business_type") or business_type,
                layer_name=response.get("layer_name"),
                demographic_metrics=response.get("demographic_metrics"),
                filters=response.get("filters"),
                raw_query=user_query,
                confidence=response.get("confidence", 0.5),
                explanation=response.get("explanation", "")
            )
            
        except Exception as e:
            logger.error(f"Failed to parse map command: {e}")
            return MapCommand(
                command_type=MapCommandType.UNKNOWN,
                raw_query=user_query,
                confidence=0.0,
                explanation=f"Failed to parse command: {str(e)}"
            )
    
    def parse_simple(self, user_query: str) -> MapCommand:
        """Simple rule-based parsing for common commands (no LLM needed)"""
        query_lower = user_query.lower().strip()
        
        if any(word in query_lower for word in ["competition", "competitors", "competing"]):
            return MapCommand(
                command_type=MapCommandType.SHOW_COMPETITION,
                raw_query=user_query,
                confidence=0.8,
                explanation="Showing nearby competitors"
            )
        
        if any(word in query_lower for word in ["demographics", "population", "income", "census"]):
            metrics = []
            if "population" in query_lower:
                metrics.append("population")
            if "income" in query_lower:
                metrics.append("median_income")
            if "age" in query_lower:
                metrics.append("median_age")
            
            return MapCommand(
                command_type=MapCommandType.SHOW_DEMOGRAPHICS,
                demographic_metrics=metrics or ["population", "median_income"],
                raw_query=user_query,
                confidence=0.8,
                explanation="Showing demographic data"
            )
        
        if any(word in query_lower for word in ["compare", "versus", "vs"]):
            return MapCommand(
                command_type=MapCommandType.COMPARE_LOCATIONS,
                raw_query=user_query,
                confidence=0.6,
                explanation="Comparing locations"
            )
        
        if any(word in query_lower for word in ["heatmap", "heat map", "density"]):
            return MapCommand(
                command_type=MapCommandType.SHOW_HEATMAP,
                raw_query=user_query,
                confidence=0.8,
                explanation="Generating heatmap visualization"
            )
        
        if any(word in query_lower for word in ["clear", "remove", "hide"]):
            return MapCommand(
                command_type=MapCommandType.CLEAR_LAYER,
                raw_query=user_query,
                confidence=0.7,
                explanation="Clearing map layer"
            )
        
        if "radius" in query_lower or "miles" in query_lower:
            import re
            numbers = re.findall(r'\d+(?:\.\d+)?', query_lower)
            radius = float(numbers[0]) if numbers else None
            return MapCommand(
                command_type=MapCommandType.SET_RADIUS,
                radius_miles=radius,
                raw_query=user_query,
                confidence=0.8 if radius else 0.5,
                explanation=f"Setting radius to {radius} miles" if radius else "Setting radius"
            )
        
        return MapCommand(
            command_type=MapCommandType.UNKNOWN,
            raw_query=user_query,
            confidence=0.0,
            explanation="Could not understand the command"
        )


map_command_parser = MapCommandParser()
