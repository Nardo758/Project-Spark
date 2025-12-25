"""
Census Bureau ACS 5-Year Data Service

Fetches demographic data from the Census Bureau API for market intelligence.
Uses American Community Survey (ACS) 5-Year Data (most granular, down to block-group level).

Key Variables:
- B01003_001E: Total population
- B01002_001E: Median age
- B19013_001E: Median household income
- B19301_001E: Per capita income
- B17001_002E: Population below poverty line
- B23025_005E: Unemployed count
- B23025_002E: Labor force (for unemployment rate)
- B11001_001E: Total households
- B11001_003E: Family households
- B25077_001E: Median home value
- B25064_001E: Median gross rent
- B15003_022E-025E: Educational attainment (Bachelor's+)
- B08301_019E: Work from home
"""

import os
import httpx
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class CensusDataService:
    BASE_URL = "https://api.census.gov/data"
    DATASET = "acs/acs5"
    DEFAULT_YEAR = 2023
    
    VARIABLES = [
        "B01003_001E",  # Total population
        "B01002_001E",  # Median age
        "B19013_001E",  # Median household income
        "B19301_001E",  # Per capita income
        "B17001_002E",  # Population below poverty
        "B23025_005E",  # Unemployed
        "B23025_002E",  # Labor force
        "B11001_001E",  # Total households
        "B11001_003E",  # Family households
        "B25077_001E",  # Median home value
        "B25064_001E",  # Median gross rent
        "B15003_022E",  # Bachelor's degree
        "B15003_023E",  # Master's degree
        "B15003_024E",  # Professional degree
        "B15003_025E",  # Doctorate degree
        "B08301_019E",  # Work from home
    ]
    
    VARIABLE_LABELS = {
        "B01003_001E": "population",
        "B01002_001E": "median_age",
        "B19013_001E": "median_income",
        "B19301_001E": "per_capita_income",
        "B17001_002E": "poverty_population",
        "B23025_005E": "unemployed",
        "B23025_002E": "labor_force",
        "B11001_001E": "households",
        "B11001_003E": "family_households",
        "B25077_001E": "median_home_value",
        "B25064_001E": "median_rent",
        "B15003_022E": "bachelors",
        "B15003_023E": "masters",
        "B15003_024E": "professional",
        "B15003_025E": "doctorate",
        "B08301_019E": "work_from_home",
    }
    
    def __init__(self):
        self.api_key = os.getenv("CENSUS_API_KEY")
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = timedelta(days=30)  # Cache for 30 days
    
    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)
    
    def _get_cache_key(self, geography_type: str, geography_id: str) -> str:
        return f"{geography_type}:{geography_id}"
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        if cache_key not in self._cache:
            return False
        cached = self._cache[cache_key]
        fetched_at = cached.get("fetched_at")
        if not fetched_at:
            return False
        return datetime.now() - datetime.fromisoformat(fetched_at) < self._cache_ttl
    
    async def fetch_by_zipcode(self, zip_code: str, year: int = None) -> Optional[Dict[str, Any]]:
        """
        Fetch ACS 5-Year data for a ZIP Code Tabulation Area (ZCTA).
        
        Args:
            zip_code: 5-digit ZIP code
            year: Data year (default: 2023)
        
        Returns:
            Dictionary with demographic data or None if not found
        """
        if not self.is_configured:
            logger.warning("Census API key not configured")
            return None
        
        year = year or self.DEFAULT_YEAR
        cache_key = self._get_cache_key("zcta", zip_code)
        
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]["data"]
        
        variables = ",".join(self.VARIABLES)
        url = f"{self.BASE_URL}/{year}/{self.DATASET}?get={variables}&for=zip%20code%20tabulation%20area:{zip_code}&key={self.api_key}"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                
                if response.status_code == 204:
                    logger.info(f"No data found for ZIP {zip_code}")
                    return None
                
                response.raise_for_status()
                data = response.json()
                
                if len(data) < 2:
                    return None
                
                result = self._parse_response(data)
                result["geography_type"] = "zcta"
                result["geography_id"] = zip_code
                result["fetched_at"] = datetime.now().isoformat()
                result["year"] = year
                
                self._cache[cache_key] = {
                    "data": result,
                    "fetched_at": datetime.now().isoformat()
                }
                
                return result
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Census API error for ZIP {zip_code}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching Census data for ZIP {zip_code}: {e}")
            return None
    
    async def fetch_by_state(self, state_fips: str, year: int = None) -> Optional[Dict[str, Any]]:
        """
        Fetch ACS 5-Year data for a state.
        
        Args:
            state_fips: 2-digit state FIPS code (e.g., "06" for California)
            year: Data year (default: 2023)
        """
        if not self.is_configured:
            return None
        
        year = year or self.DEFAULT_YEAR
        cache_key = self._get_cache_key("state", state_fips)
        
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]["data"]
        
        variables = ",".join(self.VARIABLES)
        url = f"{self.BASE_URL}/{year}/{self.DATASET}?get={variables}&for=state:{state_fips}&key={self.api_key}"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                
                if len(data) < 2:
                    return None
                
                result = self._parse_response(data)
                result["geography_type"] = "state"
                result["geography_id"] = state_fips
                result["fetched_at"] = datetime.now().isoformat()
                result["year"] = year
                
                self._cache[cache_key] = {
                    "data": result,
                    "fetched_at": datetime.now().isoformat()
                }
                
                return result
                
        except Exception as e:
            logger.error(f"Error fetching Census data for state {state_fips}: {e}")
            return None
    
    async def fetch_by_county(self, state_fips: str, county_fips: str, year: int = None) -> Optional[Dict[str, Any]]:
        """
        Fetch ACS 5-Year data for a county.
        
        Args:
            state_fips: 2-digit state FIPS code
            county_fips: 3-digit county FIPS code
            year: Data year (default: 2023)
        """
        if not self.is_configured:
            return None
        
        year = year or self.DEFAULT_YEAR
        geo_id = f"{state_fips}{county_fips}"
        cache_key = self._get_cache_key("county", geo_id)
        
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]["data"]
        
        variables = ",".join(self.VARIABLES)
        url = f"{self.BASE_URL}/{year}/{self.DATASET}?get={variables}&for=county:{county_fips}&in=state:{state_fips}&key={self.api_key}"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                
                if len(data) < 2:
                    return None
                
                result = self._parse_response(data)
                result["geography_type"] = "county"
                result["geography_id"] = geo_id
                result["fetched_at"] = datetime.now().isoformat()
                result["year"] = year
                
                self._cache[cache_key] = {
                    "data": result,
                    "fetched_at": datetime.now().isoformat()
                }
                
                return result
                
        except Exception as e:
            logger.error(f"Error fetching Census data for county {geo_id}: {e}")
            return None
    
    def _parse_response(self, data: list) -> Dict[str, Any]:
        """Parse Census API response into a clean dictionary."""
        headers = data[0]
        values = data[1]
        
        result = {}
        
        for i, header in enumerate(headers):
            if header in self.VARIABLE_LABELS:
                label = self.VARIABLE_LABELS[header]
                value = values[i]
                try:
                    if value is None or value == "" or value == "-":
                        result[label] = None
                    else:
                        result[label] = float(value) if "." in str(value) else int(value)
                except (ValueError, TypeError):
                    result[label] = None
        
        # Calculate derived metrics
        result = self._calculate_derived_metrics(result)
        
        return result
    
    def _calculate_derived_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate derived metrics from raw Census data."""
        
        # Poverty rate
        poverty_pop = data.get("poverty_population")
        population = data.get("population")
        if poverty_pop is not None and population and population > 0:
            data["poverty_rate"] = round((poverty_pop / population) * 100, 1)
        else:
            data["poverty_rate"] = None
        
        # Unemployment rate
        unemployed = data.get("unemployed")
        labor_force = data.get("labor_force")
        if unemployed is not None and labor_force and labor_force > 0:
            data["unemployment_rate"] = round((unemployed / labor_force) * 100, 1)
        else:
            data["unemployment_rate"] = None
        
        # Bachelor's degree or higher percentage
        bachelors = data.get("bachelors") or 0
        masters = data.get("masters") or 0
        professional = data.get("professional") or 0
        doctorate = data.get("doctorate") or 0
        educated = bachelors + masters + professional + doctorate
        
        if population and population > 0:
            data["bachelors_or_higher"] = educated
            data["bachelors_or_higher_pct"] = round((educated / population) * 100, 1)
        else:
            data["bachelors_or_higher"] = None
            data["bachelors_or_higher_pct"] = None
        
        # Work from home percentage
        wfh = data.get("work_from_home")
        if wfh is not None and population and population > 0:
            data["work_from_home_pct"] = round((wfh / population) * 100, 1)
        else:
            data["work_from_home_pct"] = None
        
        # Family household percentage
        family = data.get("family_households")
        households = data.get("households")
        if family is not None and households and households > 0:
            data["family_household_pct"] = round((family / households) * 100, 1)
        else:
            data["family_household_pct"] = None
        
        # Purchasing power estimate (households × median income)
        if households and data.get("median_income"):
            data["purchasing_power"] = households * data["median_income"]
        else:
            data["purchasing_power"] = None
        
        return data
    
    def calculate_enhanced_signal_score(self, base_score: float, demographics: Dict[str, Any]) -> float:
        """
        Enhance opportunity signal score with demographic context.
        
        Uses population, income, and underserved indicators to adjust scoring.
        """
        if not demographics:
            return base_score
        
        # Population multiplier (0.5 to 2.0)
        population = demographics.get("population", 0)
        population_multiplier = min(max(population / 50000, 0.5), 2.0)
        
        # Income multiplier (0.5 to 1.5)
        median_income = demographics.get("median_income", 75000)
        income_multiplier = min(max(median_income / 75000, 0.5), 1.5)
        
        # Underserved bonus (areas with higher poverty or unemployment)
        poverty_rate = demographics.get("poverty_rate", 0) or 0
        unemployment_rate = demographics.get("unemployment_rate", 0) or 0
        
        if poverty_rate > 15 or unemployment_rate > 8:
            underserved_bonus = 1.2
        elif poverty_rate > 10 or unemployment_rate > 6:
            underserved_bonus = 1.1
        else:
            underserved_bonus = 1.0
        
        enhanced_score = base_score * population_multiplier * income_multiplier * underserved_bonus
        
        return min(round(enhanced_score, 1), 100)


# Singleton instance
census_service = CensusDataService()
