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
    
    EXTENDED_VARIABLES = [
        "B19001_002E",  # Income < $10k
        "B19001_003E",  # Income $10k-$15k
        "B19001_004E",  # Income $15k-$20k
        "B19001_005E",  # Income $20k-$25k
        "B19001_006E",  # Income $25k-$30k
        "B19001_007E",  # Income $30k-$35k
        "B19001_008E",  # Income $35k-$40k
        "B19001_009E",  # Income $40k-$45k
        "B19001_010E",  # Income $45k-$50k
        "B19001_011E",  # Income $50k-$60k
        "B19001_012E",  # Income $60k-$75k
        "B19001_013E",  # Income $75k-$100k
        "B19001_014E",  # Income $100k-$125k
        "B19001_015E",  # Income $125k-$150k
        "B19001_016E",  # Income $150k-$200k
        "B19001_017E",  # Income $200k+
        "B01001_003E",  # Male under 5
        "B01001_004E",  # Male 5-9
        "B01001_005E",  # Male 10-14
        "B01001_006E",  # Male 15-17
        "B01001_007E",  # Male 18-19
        "B01001_008E",  # Male 20
        "B01001_009E",  # Male 21
        "B01001_010E",  # Male 22-24
        "B01001_011E",  # Male 25-29
        "B01001_012E",  # Male 30-34
        "B01001_013E",  # Male 35-39
        "B01001_014E",  # Male 40-44
        "B01001_015E",  # Male 45-49
        "B01001_016E",  # Male 50-54
        "B01001_017E",  # Male 55-59
        "B01001_018E",  # Male 60-61
        "B01001_019E",  # Male 62-64
        "B01001_020E",  # Male 65-66
        "B01001_021E",  # Male 67-69
        "B01001_022E",  # Male 70-74
        "B01001_023E",  # Male 75-79
        "B01001_024E",  # Male 80-84
        "B01001_025E",  # Male 85+
        "B01001_027E",  # Female under 5
        "B01001_028E",  # Female 5-9
        "B01001_029E",  # Female 10-14
        "B01001_030E",  # Female 15-17
        "B01001_031E",  # Female 18-19
        "B01001_032E",  # Female 20
        "B01001_033E",  # Female 21
        "B01001_034E",  # Female 22-24
        "B01001_035E",  # Female 25-29
        "B01001_036E",  # Female 30-34
        "B01001_037E",  # Female 35-39
        "B01001_038E",  # Female 40-44
        "B01001_039E",  # Female 45-49
        "B01001_040E",  # Female 50-54
        "B01001_041E",  # Female 55-59
        "B01001_042E",  # Female 60-61
        "B01001_043E",  # Female 62-64
        "B01001_044E",  # Female 65-66
        "B01001_045E",  # Female 67-69
        "B01001_046E",  # Female 70-74
        "B01001_047E",  # Female 75-79
        "B01001_048E",  # Female 80-84
        "B01001_049E",  # Female 85+
        "B08303_001E",  # Total commuters
        "B08303_002E",  # Commute < 5 min
        "B08303_003E",  # Commute 5-9 min
        "B08303_004E",  # Commute 10-14 min
        "B08303_005E",  # Commute 15-19 min
        "B08303_006E",  # Commute 20-24 min
        "B08303_007E",  # Commute 25-29 min
        "B08303_008E",  # Commute 30-34 min
        "B08303_009E",  # Commute 35-39 min
        "B08303_010E",  # Commute 40-44 min
        "B08303_011E",  # Commute 45-59 min
        "B08303_012E",  # Commute 60-89 min
        "B08303_013E",  # Commute 90+ min
        "B28002_001E",  # Total households (internet)
        "B28002_002E",  # With internet subscription
        "B28002_004E",  # With broadband
        "B28002_007E",  # Without internet
        "B25003_001E",  # Total housing units
        "B25003_002E",  # Owner occupied
        "B25003_003E",  # Renter occupied
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
    
    INCOME_BRACKETS = [
        ("under_10k", "B19001_002E"),
        ("10k_15k", "B19001_003E"),
        ("15k_20k", "B19001_004E"),
        ("20k_25k", "B19001_005E"),
        ("25k_30k", "B19001_006E"),
        ("30k_35k", "B19001_007E"),
        ("35k_40k", "B19001_008E"),
        ("40k_45k", "B19001_009E"),
        ("45k_50k", "B19001_010E"),
        ("50k_60k", "B19001_011E"),
        ("60k_75k", "B19001_012E"),
        ("75k_100k", "B19001_013E"),
        ("100k_125k", "B19001_014E"),
        ("125k_150k", "B19001_015E"),
        ("150k_200k", "B19001_016E"),
        ("200k_plus", "B19001_017E"),
    ]
    
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
    
    async def fetch_extended_demographics(
        self,
        state_fips: str,
        county_fips: str,
        year: int = None
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch extended demographic data including income distribution, 
        age distribution, commute patterns, and internet access.
        
        Args:
            state_fips: 2-digit state FIPS code
            county_fips: 3-digit county FIPS code
            year: Data year (default: 2023)
        
        Returns:
            Dictionary with extended demographic breakdowns
        """
        if not self.is_configured:
            logger.warning("Census API key not configured")
            return None
        
        year = year or self.DEFAULT_YEAR
        
        chunk_size = 25
        all_raw = {}
        
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=False) as client:
                for i in range(0, len(self.EXTENDED_VARIABLES), chunk_size):
                    chunk = self.EXTENDED_VARIABLES[i:i+chunk_size]
                    variables = ",".join(chunk)
                    url = f"{self.BASE_URL}/{year}/{self.DATASET}?get={variables}&for=county:{county_fips}&in=state:{state_fips}&key={self.api_key}"
                    
                    response = await client.get(url)
                    
                    if response.status_code == 302:
                        location = response.headers.get("location", "")
                        if "invalid_key" in location:
                            logger.error("Census API key is invalid")
                            return None
                        return None
                    
                    if response.status_code == 204 or response.status_code == 404:
                        continue
                    
                    response.raise_for_status()
                    data = response.json()
                    
                    if len(data) >= 2:
                        headers = data[0]
                        values = data[1]
                        for j, header in enumerate(headers):
                            if header not in ["state", "county"]:
                                try:
                                    val = values[j]
                                    if val is None or val == "" or val == "-":
                                        all_raw[header] = None
                                    else:
                                        all_raw[header] = int(val) if str(val).lstrip('-').isdigit() else float(val)
                                except (ValueError, TypeError):
                                    all_raw[header] = None
                
                if not all_raw:
                    return None
                
                result = self._parse_extended_demographics_from_raw(all_raw)
                result["geography_type"] = "county"
                result["geography_id"] = f"{state_fips}{county_fips}"
                result["fetched_at"] = datetime.now().isoformat()
                result["year"] = year
                
                return result
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Census extended API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching extended Census data: {e}")
            return None
    
    def _parse_extended_demographics(self, data: list) -> Dict[str, Any]:
        """Parse extended demographics response into structured data."""
        headers = data[0]
        values = data[1]
        
        raw = {}
        for i, header in enumerate(headers):
            try:
                val = values[i]
                if val is None or val == "" or val == "-":
                    raw[header] = None
                else:
                    raw[header] = int(val) if str(val).lstrip('-').isdigit() else float(val)
            except (ValueError, TypeError, AttributeError):
                raw[header] = None
        
        return self._parse_extended_demographics_from_raw(raw)
    
    def _parse_extended_demographics_from_raw(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """Parse raw Census data into structured extended demographics."""
        result = {}
        
        income_distribution = {}
        for label, var in self.INCOME_BRACKETS:
            income_distribution[label] = raw.get(var)
        result["income_distribution"] = income_distribution
        
        total_hh = sum(v for v in income_distribution.values() if v)
        if total_hh > 0:
            result["income_distribution_pct"] = {
                k: round((v / total_hh) * 100, 1) if v else 0
                for k, v in income_distribution.items()
            }
            result["income_under_50k"] = sum(
                income_distribution.get(k, 0) or 0 
                for k in ["under_10k", "10k_15k", "15k_20k", "20k_25k", "25k_30k", "30k_35k", "35k_40k", "40k_45k", "45k_50k"]
            )
            result["income_50k_100k"] = sum(
                income_distribution.get(k, 0) or 0 
                for k in ["50k_60k", "60k_75k", "75k_100k"]
            )
            result["income_100k_plus"] = sum(
                income_distribution.get(k, 0) or 0 
                for k in ["100k_125k", "125k_150k", "150k_200k", "200k_plus"]
            )
        
        male_under_18 = sum(raw.get(f"B01001_{str(i).zfill(3)}E", 0) or 0 for i in range(3, 7))
        male_18_24 = sum(raw.get(f"B01001_{str(i).zfill(3)}E", 0) or 0 for i in range(7, 11))
        male_25_44 = sum(raw.get(f"B01001_{str(i).zfill(3)}E", 0) or 0 for i in range(11, 15))
        male_45_64 = sum(raw.get(f"B01001_{str(i).zfill(3)}E", 0) or 0 for i in range(15, 20))
        male_65_plus = sum(raw.get(f"B01001_{str(i).zfill(3)}E", 0) or 0 for i in range(20, 26))
        
        female_under_18 = sum(raw.get(f"B01001_{str(i).zfill(3)}E", 0) or 0 for i in range(27, 31))
        female_18_24 = sum(raw.get(f"B01001_{str(i).zfill(3)}E", 0) or 0 for i in range(31, 35))
        female_25_44 = sum(raw.get(f"B01001_{str(i).zfill(3)}E", 0) or 0 for i in range(35, 39))
        female_45_64 = sum(raw.get(f"B01001_{str(i).zfill(3)}E", 0) or 0 for i in range(39, 44))
        female_65_plus = sum(raw.get(f"B01001_{str(i).zfill(3)}E", 0) or 0 for i in range(44, 50))
        
        result["age_distribution"] = {
            "under_18": male_under_18 + female_under_18,
            "18_24": male_18_24 + female_18_24,
            "25_44": male_25_44 + female_25_44,
            "45_64": male_45_64 + female_45_64,
            "65_plus": male_65_plus + female_65_plus,
        }
        
        total_commuters = raw.get("B08303_001E") or 0
        short_commute = sum(raw.get(f"B08303_{str(i).zfill(3)}E", 0) or 0 for i in range(2, 6))
        medium_commute = sum(raw.get(f"B08303_{str(i).zfill(3)}E", 0) or 0 for i in range(6, 9))
        long_commute = sum(raw.get(f"B08303_{str(i).zfill(3)}E", 0) or 0 for i in range(9, 14))
        
        result["commute_patterns"] = {
            "total_commuters": total_commuters,
            "under_20_min": short_commute,
            "20_34_min": medium_commute,
            "35_plus_min": long_commute,
        }
        if total_commuters > 0:
            result["commute_patterns"]["under_20_min_pct"] = round((short_commute / total_commuters) * 100, 1)
            result["commute_patterns"]["long_commute_pct"] = round((long_commute / total_commuters) * 100, 1)
        
        internet_total = raw.get("B28002_001E") or 0
        internet_sub = raw.get("B28002_002E") or 0
        broadband = raw.get("B28002_004E") or 0
        no_internet = raw.get("B28002_007E") or 0
        
        result["internet_access"] = {
            "total_households": internet_total,
            "with_internet": internet_sub,
            "with_broadband": broadband,
            "without_internet": no_internet,
        }
        if internet_total > 0:
            result["internet_access"]["internet_pct"] = round((internet_sub / internet_total) * 100, 1)
            result["internet_access"]["broadband_pct"] = round((broadband / internet_total) * 100, 1)
        
        housing_total = raw.get("B25003_001E") or 0
        owner_occupied = raw.get("B25003_002E") or 0
        renter_occupied = raw.get("B25003_003E") or 0
        
        result["housing_tenure"] = {
            "total_units": housing_total,
            "owner_occupied": owner_occupied,
            "renter_occupied": renter_occupied,
        }
        if housing_total > 0:
            result["housing_tenure"]["owner_pct"] = round((owner_occupied / housing_total) * 100, 1)
            result["housing_tenure"]["renter_pct"] = round((renter_occupied / housing_total) * 100, 1)
        
        return result
    
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
