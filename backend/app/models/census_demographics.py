"""
Census Demographics Models

Tables for storing population dynamics, migration flows, and market growth trajectories
for enhanced geographic intelligence and opportunity scoring.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class GrowthCategory(str, enum.Enum):
    BOOMING = "booming"
    GROWING = "growing"
    STABLE = "stable"
    DECLINING = "declining"


class CensusPopulationEstimate(Base):
    """
    Annual population estimates by geography from Census Bureau PEP data.
    Used for tracking growth trends and market sizing.
    """
    __tablename__ = "census_population_estimates"
    
    id = Column(Integer, primary_key=True, index=True)
    state_fips = Column(String(2), nullable=False, index=True)
    county_fips = Column(String(3), nullable=True, index=True)
    place_fips = Column(String(5), nullable=True)
    geography_name = Column(String(255), nullable=False)
    geography_type = Column(String(50), nullable=False)
    
    year = Column(Integer, nullable=False, index=True)
    population = Column(Integer, nullable=False)
    population_estimate = Column(Integer, nullable=True)
    births = Column(Integer, nullable=True)
    deaths = Column(Integer, nullable=True)
    natural_increase = Column(Integer, nullable=True)
    net_domestic_migration = Column(Integer, nullable=True)
    net_international_migration = Column(Integer, nullable=True)
    
    yoy_growth_rate = Column(Float, nullable=True)
    five_year_growth_rate = Column(Float, nullable=True)
    
    median_age = Column(Float, nullable=True)
    median_income = Column(Integer, nullable=True)
    
    demographics_snapshot = Column(JSONB, nullable=True)
    
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())
    source_api = Column(String(100), default="Census PEP")
    
    __table_args__ = (
        {'postgresql_partition_by': None},
    )


class CensusMigrationFlow(Base):
    """
    County-to-county and state-to-state migration flows from ACS data.
    Used for identifying emerging markets and population movement patterns.
    """
    __tablename__ = "census_migration_flows"
    
    id = Column(Integer, primary_key=True, index=True)
    
    origin_state_fips = Column(String(2), nullable=False, index=True)
    origin_county_fips = Column(String(3), nullable=True)
    origin_name = Column(String(255), nullable=False)
    
    destination_state_fips = Column(String(2), nullable=False, index=True)
    destination_county_fips = Column(String(3), nullable=True)
    destination_name = Column(String(255), nullable=False)
    
    year = Column(Integer, nullable=False, index=True)
    flow_count = Column(Integer, nullable=False)
    margin_of_error = Column(Integer, nullable=True)
    
    migration_type = Column(String(50), default="domestic")
    
    origin_median_income = Column(Integer, nullable=True)
    destination_median_income = Column(Integer, nullable=True)
    income_differential = Column(Integer, nullable=True)
    
    flow_characteristics = Column(JSONB, nullable=True)
    
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())
    source_api = Column(String(100), default="Census ACS Flows")


class MarketGrowthTrajectory(Base):
    """
    Computed market growth trajectories combining population, economic, and signal data.
    Used for overlay visualization and opportunity scoring adjustments.
    """
    __tablename__ = "market_growth_trajectories"
    
    id = Column(Integer, primary_key=True, index=True)
    
    state_fips = Column(String(2), nullable=False, index=True)
    county_fips = Column(String(3), nullable=True, index=True)
    city = Column(String(255), nullable=True, index=True)
    region = Column(String(100), nullable=True)
    geography_name = Column(String(255), nullable=False)
    
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    growth_category = Column(SQLEnum(GrowthCategory), nullable=False, default=GrowthCategory.STABLE)
    growth_score = Column(Float, nullable=False, default=50.0)
    
    population_growth_rate = Column(Float, nullable=True)
    job_growth_rate = Column(Float, nullable=True)
    income_growth_rate = Column(Float, nullable=True)
    business_formation_rate = Column(Float, nullable=True)
    
    net_migration_rate = Column(Float, nullable=True)
    migration_trend = Column(String(20), nullable=True)
    
    opportunity_signal_count = Column(Integer, default=0)
    avg_opportunity_score = Column(Float, nullable=True)
    signal_density_percentile = Column(Float, nullable=True)
    
    housing_growth_rate = Column(Float, nullable=True)
    commercial_growth_rate = Column(Float, nullable=True)
    
    trajectory_factors = Column(JSONB, nullable=True)
    
    data_year = Column(Integer, nullable=False)
    computed_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    is_active = Column(Boolean, default=True)
    confidence_level = Column(Float, default=0.8)


class ServiceAreaBoundary(Base):
    """
    Dynamically computed service area boundaries for opportunities.
    Generated using signal clustering + demographic validation.
    """
    __tablename__ = "service_area_boundaries"
    
    id = Column(Integer, primary_key=True, index=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id"), nullable=False, index=True)
    
    boundary_type = Column(String(50), default="computed")
    
    center_latitude = Column(Float, nullable=False)
    center_longitude = Column(Float, nullable=False)
    radius_miles = Column(Float, nullable=True)
    
    geojson_polygon = Column(JSONB, nullable=True)
    
    included_counties = Column(JSONB, nullable=True)
    included_cities = Column(JSONB, nullable=True)
    
    total_population = Column(Integer, nullable=True)
    total_households = Column(Integer, nullable=True)
    median_income = Column(Integer, nullable=True)
    
    signal_count = Column(Integer, default=0)
    signal_density = Column(Float, nullable=True)
    
    market_penetration_estimate = Column(Float, nullable=True)
    addressable_market_value = Column(Float, nullable=True)
    
    computation_factors = Column(JSONB, nullable=True)
    
    computed_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    
    opportunity = relationship("Opportunity", back_populates="service_areas")
