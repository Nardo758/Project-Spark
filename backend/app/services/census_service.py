"""
Census Bureau Data Service

Fetches demographic and population dynamics data from Census Bureau APIs:

1. ACS 5-Year Data - Demographics (most granular, down to block-group level)
2. Population Estimates API - Current population and migration components
3. ACS Migration Flows - County-to-county migration patterns

Key Variables (ACS 5-Year):
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

Population Estimates Variables:
- POP: Total population
- DENSITY: Population density
- BIRTHS: Number of births
- DEATHS: Number of deaths
- NATURALINC: Natural increase (births - deaths)
- DOMESTICMIG: Net domestic migration
- INTERNATIONALMIG: Net international migration
- NETMIG: Total net migration
"""

import os
import httpx
from typing import Optional, Dict, Any, List
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
    
    async def fetch_population_estimates(
        self, 
        state_fips: str = None, 
        county_fips: str = None, 
        year: int = 2023
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch Population Estimates data using the PEP charv endpoint.
        
        The Census PEP API changed structure - now uses /pep/charv with YEAR parameter.
        
        Args:
            state_fips: 2-digit state FIPS code (optional, returns all states if None)
            county_fips: 3-digit county FIPS code (optional)
            year: Data year (default: 2023 - latest stable vintage)
        
        Returns:
            List of dictionaries with population data
        """
        if not self.is_configured:
            logger.warning("Census API key not configured")
            return None
        
        variables = "NAME,POP"
        
        if county_fips and state_fips:
            geo = f"for=county:{county_fips}&in=state:{state_fips}"
        elif state_fips:
            geo = f"for=county:*&in=state:{state_fips}"
        else:
            geo = "for=county:*"
        
        vintage = 2023
        url = f"{self.BASE_URL}/{vintage}/pep/charv?get={variables}&{geo}&YEAR={year}&key={self.api_key}"
        
        try:
            async with httpx.AsyncClient(timeout=60.0, follow_redirects=False) as client:
                response = await client.get(url)
                
                if response.status_code == 302:
                    location = response.headers.get("location", "")
                    if "invalid_key" in location:
                        logger.error("Census API key is invalid or not yet activated")
                        return None
                    logger.warning(f"Redirect to: {location}")
                    return None
                
                if response.status_code == 204 or response.status_code == 404:
                    logger.info(f"No population estimates data found for year {year}")
                    return None
                
                if response.status_code == 400:
                    logger.warning(f"Bad request for PEP data - may be unsupported geography or year")
                    return None
                
                response.raise_for_status()
                data = response.json()
                
                if len(data) < 2:
                    return None
                
                results = self._parse_population_estimates(data)
                return results
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Census Population Estimates API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching population estimates: {e}")
            return None
    
    def _parse_population_estimates(self, data: list) -> List[Dict[str, Any]]:
        """Parse Population Estimates API response."""
        headers = data[0]
        results = []
        
        for row in data[1:]:
            record = {}
            for i, header in enumerate(headers):
                value = row[i]
                if header == "NAME":
                    record["name"] = value
                elif header == "state":
                    record["state_fips"] = value
                elif header == "county":
                    record["county_fips"] = value
                else:
                    try:
                        if value is None or value == "" or value == "-":
                            record[header.lower()] = None
                        else:
                            record[header.lower()] = float(value) if "." in str(value) else int(value)
                    except (ValueError, TypeError):
                        record[header.lower()] = None
            
            record["fetched_at"] = datetime.now().isoformat()
            results.append(record)
        
        return results
    
    async def fetch_population_history(
        self, 
        state_fips: str, 
        county_fips: str, 
        start_year: int = 2020, 
        end_year: int = 2023
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch historical population data for growth trend analysis.
        
        Uses Census PEP 2023 vintage which covers 2020-2023.
        
        Args:
            state_fips: 2-digit state FIPS code
            county_fips: 3-digit county FIPS code
            start_year: First year to fetch (default: 2020)
            end_year: Last year to fetch (default: 2023)
        
        Returns:
            List of yearly population data with growth rates
        """
        if not self.is_configured:
            return None
        
        history = []
        
        for year in range(start_year, end_year + 1):
            data = await self.fetch_population_estimates(state_fips, county_fips, year)
            if data and len(data) > 0:
                record = data[0]
                record["year"] = year
                history.append(record)
        
        if len(history) >= 2:
            for i in range(1, len(history)):
                prev_pop = history[i-1].get("pop")
                curr_pop = history[i].get("pop")
                if prev_pop and curr_pop and prev_pop > 0:
                    growth_rate = ((curr_pop - prev_pop) / prev_pop) * 100
                    history[i]["yoy_growth_rate"] = round(growth_rate, 2)
                else:
                    history[i]["yoy_growth_rate"] = None
            
            first_pop = history[0].get("pop")
            last_pop = history[-1].get("pop")
            years = len(history) - 1
            if first_pop and last_pop and first_pop > 0 and years > 0:
                cagr = ((last_pop / first_pop) ** (1 / years) - 1) * 100
                for record in history:
                    record["cagr"] = round(cagr, 2)
        
        return history
    
    async def fetch_migration_flows(
        self, 
        state_fips: str, 
        county_fips: str, 
        year: int = 2022
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch ACS Migration Flows data for county-to-county migration.
        
        Args:
            state_fips: 2-digit state FIPS code
            county_fips: 3-digit county FIPS code
            year: Data year (default: 2022 - latest available)
        
        Returns:
            Dictionary with migration flow data including top origins
        """
        if not self.is_configured:
            logger.warning("Census API key not configured")
            return None
        
        variables = "MOVEDIN,MOVEDOUT,MOVEDNET,GEOID1,FULL1_NAME,GEOID2,FULL2_NAME"
        url = f"{self.BASE_URL}/{year}/acs/flows?get={variables}&for=county:{county_fips}&in=state:{state_fips}&key={self.api_key}"
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(url)
                
                if response.status_code == 204:
                    logger.info(f"No migration flow data found for {state_fips}-{county_fips}")
                    return None
                
                if response.status_code == 400:
                    logger.warning(f"Migration flows API returned 400 - data may not be available for this geography")
                    return None
                
                response.raise_for_status()
                data = response.json()
                
                if len(data) < 2:
                    return None
                
                result = self._parse_migration_flows(data, state_fips, county_fips)
                return result
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Census Migration Flows API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching migration flows: {e}")
            return None
    
    def _parse_migration_flows(self, data: list, state_fips: str, county_fips: str) -> Dict[str, Any]:
        """Parse ACS Migration Flows API response."""
        headers = data[0]
        
        total_moved_in = 0
        total_moved_out = 0
        origins = []
        
        for row in data[1:]:
            record = {}
            for i, header in enumerate(headers):
                value = row[i]
                if header in ["MOVEDIN", "MOVEDOUT", "MOVEDNET"]:
                    try:
                        record[header.lower()] = int(value) if value and value != "-" else 0
                    except (ValueError, TypeError):
                        record[header.lower()] = 0
                elif header == "GEOID1":
                    record["origin_geoid"] = value
                elif header == "FULL1_NAME":
                    record["origin_name"] = value
                elif header == "GEOID2":
                    record["destination_geoid"] = value
                elif header == "FULL2_NAME":
                    record["destination_name"] = value
            
            if record.get("movedin", 0) > 0:
                origins.append({
                    "origin_geoid": record.get("origin_geoid"),
                    "origin_name": record.get("origin_name"),
                    "moved_in": record.get("movedin", 0)
                })
                total_moved_in += record.get("movedin", 0)
            
            total_moved_out += record.get("movedout", 0)
        
        origins.sort(key=lambda x: x["moved_in"], reverse=True)
        
        return {
            "state_fips": state_fips,
            "county_fips": county_fips,
            "total_moved_in": total_moved_in,
            "total_moved_out": total_moved_out,
            "net_migration": total_moved_in - total_moved_out,
            "top_origins": origins[:20],
            "fetched_at": datetime.now().isoformat()
        }
    
    async def get_population_dynamics(
        self, 
        state_fips: str, 
        county_fips: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive population dynamics data for a county.
        
        Combines current estimates, historical trends, and migration patterns.
        
        Args:
            state_fips: 2-digit state FIPS code
            county_fips: 3-digit county FIPS code
        
        Returns:
            Dictionary with all population dynamics data
        """
        if not self.is_configured:
            return None
        
        current = await self.fetch_population_estimates(state_fips, county_fips, 2023)
        history = await self.fetch_population_history(state_fips, county_fips)
        migration = await self.fetch_migration_flows(state_fips, county_fips)
        
        demographics = await self.fetch_by_county(state_fips, county_fips)
        
        result = {
            "state_fips": state_fips,
            "county_fips": county_fips,
            "current_population": current[0] if current else None,
            "population_history": history,
            "migration_flows": migration,
            "demographics": demographics,
            "fetched_at": datetime.now().isoformat()
        }
        
        if history and len(history) >= 2:
            result["summary"] = {
                "current_pop": history[-1].get("pop") if history else None,
                "cagr": history[-1].get("cagr") if history else None,
                "latest_yoy_growth": history[-1].get("yoy_growth_rate") if history else None,
                "net_migration": history[-1].get("netmig") if history else None,
                "domestic_migration": history[-1].get("domesticmig") if history else None,
                "international_migration": history[-1].get("internationalmig") if history else None,
                "growth_classification": self._classify_growth(history[-1].get("cagr") if history else None)
            }
        
        return result
    
    def _classify_growth(self, cagr: Optional[float]) -> str:
        """Classify growth rate for opportunity analysis."""
        if cagr is None:
            return "unknown"
        if cagr >= 3:
            return "booming"
        elif cagr >= 1.5:
            return "fast_growing"
        elif cagr >= 0.5:
            return "growing"
        elif cagr >= 0:
            return "stable"
        elif cagr >= -1:
            return "declining"
        else:
            return "shrinking"


# Singleton instance
census_service = CensusDataService()
