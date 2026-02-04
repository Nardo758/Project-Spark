"""
Derived Metrics Calculator

Calculates standardized business viability metrics from raw zone data.
All derived metrics are normalized to 0-100 scale for comparison.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import math


@dataclass
class DerivedMetric:
    """Single derived metric with raw and normalized values"""
    name: str
    raw_value: float
    normalized_value: float  # 0-100 scale
    category: str  # market, traffic, economic, demographics
    description: str
    is_higher_better: bool = True


@dataclass
class DerivedMetricsResult:
    """Complete derived metrics for a zone"""
    metrics: Dict[str, DerivedMetric] = field(default_factory=dict)
    category_scores: Dict[str, float] = field(default_factory=dict)
    overall_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'metrics': {
                k: {
                    'name': v.name,
                    'raw_value': round(v.raw_value, 2),
                    'normalized_value': round(v.normalized_value, 1),
                    'category': v.category,
                    'description': v.description,
                    'is_higher_better': v.is_higher_better
                }
                for k, v in self.metrics.items()
            },
            'category_scores': {k: round(v, 1) for k, v in self.category_scores.items()},
            'overall_score': round(self.overall_score, 1)
        }


class DerivedMetricsCalculator:
    """
    Calculates derived metrics from raw zone data.
    
    Raw metrics expected:
    - total_population: int
    - population_growth: float (percentage)
    - median_income: int
    - median_age: float
    - total_competitors: int
    - foot_traffic_monthly: int
    - drive_by_traffic_monthly: int
    """
    
    # Normalization ranges for each metric (min, max, is_higher_better)
    # Values are clamped to range before normalizing to 0-100
    NORMALIZATION_RANGES = {
        'competition_per_capita': (0, 20, False),  # Competitors per 10K pop, lower is better
        'revenue_potential_per_competitor': (0, 2000000, True),  # $ available per competitor
        'traffic_per_competitor': (0, 100000, True),  # Monthly traffic per competitor
        'foot_to_vehicle_ratio': (0, 1, True),  # 0-1 ratio, higher = more walkable
        'traffic_density': (0, 10, True),  # Traffic per capita (scaled)
        'customer_conversion_potential': (0, 100, True),  # Foot traffic % of total
        'purchasing_power_index': (0, 500, True),  # Income x Pop / 1M (can be large)
        'growth_momentum': (0, 100, True),  # Composite growth score
        'market_opportunity_score': (0, 100, True),  # Already 0-100
        'working_age_ratio': (0, 100, True),  # Already 0-100
        'income_per_traffic': (0, 200, True),  # Income per 1K traffic
    }
    
    # Category weights for overall score
    CATEGORY_WEIGHTS = {
        'market': 0.30,
        'traffic': 0.25,
        'economic': 0.30,
        'demographics': 0.15
    }
    
    def calculate(
        self,
        total_population: int,
        population_growth: float,
        median_income: int,
        median_age: float,
        total_competitors: int,
        foot_traffic_monthly: int,
        drive_by_traffic_monthly: int
    ) -> DerivedMetricsResult:
        """Calculate all derived metrics from raw zone data"""
        
        result = DerivedMetricsResult()
        total_traffic = foot_traffic_monthly + drive_by_traffic_monthly
        
        # === MARKET METRICS ===
        
        # Competition per Capita (per 10,000 residents)
        competition_per_capita = (
            (total_competitors / total_population * 10000) 
            if total_population > 0 else 0
        )
        result.metrics['competition_per_capita'] = DerivedMetric(
            name='Competition per Capita',
            raw_value=competition_per_capita,
            normalized_value=self._normalize('competition_per_capita', competition_per_capita),
            category='market',
            description='Competitors per 10,000 residents (lower is better)',
            is_higher_better=False
        )
        
        # Revenue Potential per Competitor
        total_income_pool = median_income * (total_population / 2.5)  # households
        revenue_potential = (
            total_income_pool / total_competitors 
            if total_competitors > 0 else total_income_pool
        )
        result.metrics['revenue_potential_per_competitor'] = DerivedMetric(
            name='Revenue Potential per Competitor',
            raw_value=revenue_potential,
            normalized_value=self._normalize('revenue_potential_per_competitor', revenue_potential),
            category='market',
            description='Income pool available per competitor ($)',
            is_higher_better=True
        )
        
        # Traffic per Competitor
        traffic_per_competitor = (
            total_traffic / total_competitors 
            if total_competitors > 0 else total_traffic
        )
        result.metrics['traffic_per_competitor'] = DerivedMetric(
            name='Traffic per Competitor',
            raw_value=traffic_per_competitor,
            normalized_value=self._normalize('traffic_per_competitor', traffic_per_competitor),
            category='market',
            description='Monthly visitors available per competitor',
            is_higher_better=True
        )
        
        # === TRAFFIC METRICS ===
        
        # Foot-to-Vehicle Ratio
        foot_to_vehicle = (
            foot_traffic_monthly / drive_by_traffic_monthly 
            if drive_by_traffic_monthly > 0 else 1
        )
        # Cap at 1 for normalization (equal foot/vehicle is max walkability indicator)
        foot_to_vehicle_capped = min(foot_to_vehicle, 1)
        result.metrics['foot_to_vehicle_ratio'] = DerivedMetric(
            name='Foot-to-Vehicle Ratio',
            raw_value=foot_to_vehicle,
            normalized_value=self._normalize('foot_to_vehicle_ratio', foot_to_vehicle_capped),
            category='traffic',
            description='Walkability indicator (higher = more pedestrian traffic)',
            is_higher_better=True
        )
        
        # Traffic Density (traffic per capita ratio)
        traffic_density = (
            total_traffic / total_population
            if total_population > 0 else 0
        )
        result.metrics['traffic_density'] = DerivedMetric(
            name='Traffic Density',
            raw_value=traffic_density,
            normalized_value=self._normalize('traffic_density', traffic_density),
            category='traffic',
            description='Monthly traffic per resident',
            is_higher_better=True
        )
        
        # Customer Conversion Potential (foot traffic % of total - higher = more engaged pedestrians)
        customer_conversion = (
            (foot_traffic_monthly / total_traffic) * 100
            if total_traffic > 0 else 50
        )
        result.metrics['customer_conversion_potential'] = DerivedMetric(
            name='Customer Conversion Potential',
            raw_value=customer_conversion,
            normalized_value=self._normalize('customer_conversion_potential', customer_conversion),
            category='traffic',
            description='Foot traffic % of total (higher = more engaged visitors)',
            is_higher_better=True
        )
        
        # === ECONOMIC METRICS ===
        
        # Purchasing Power Index (normalized to 0-100)
        purchasing_power = (median_income * total_population) / 1_000_000
        result.metrics['purchasing_power_index'] = DerivedMetric(
            name='Purchasing Power Index',
            raw_value=purchasing_power,
            normalized_value=self._normalize('purchasing_power_index', purchasing_power),
            category='economic',
            description='Total spending capacity (income × population)',
            is_higher_better=True
        )
        
        # Growth Momentum (population growth × traffic density)
        # Higher growth + higher activity = stronger momentum
        growth_momentum = max(0, population_growth) * traffic_density * 10
        result.metrics['growth_momentum'] = DerivedMetric(
            name='Growth Momentum',
            raw_value=growth_momentum,
            normalized_value=self._normalize('growth_momentum', growth_momentum),
            category='economic',
            description='Growth rate combined with activity level',
            is_higher_better=True
        )
        
        # Market Opportunity Score (composite)
        # High income, low competition, high traffic = high opportunity
        income_score = min(median_income / 100000, 1) * 100
        competition_score = max(0, 100 - competition_per_capita * 10)
        traffic_score = min(traffic_density * 30, 100)
        market_opportunity = (income_score * 0.4 + competition_score * 0.35 + traffic_score * 0.25)
        result.metrics['market_opportunity_score'] = DerivedMetric(
            name='Market Opportunity Score',
            raw_value=market_opportunity,
            normalized_value=self._normalize('market_opportunity_score', market_opportunity),
            category='economic',
            description='Combined income, competition, and traffic score',
            is_higher_better=True
        )
        
        # === DEMOGRAPHICS METRICS ===
        
        # Working Age Ratio (25-54 is prime spending age)
        # Estimate based on median age - closer to 40 is optimal
        age_distance = abs(median_age - 40)
        working_age_ratio = max(0, 100 - age_distance * 4)
        result.metrics['working_age_ratio'] = DerivedMetric(
            name='Working Age Ratio',
            raw_value=working_age_ratio,
            normalized_value=self._normalize('working_age_ratio', working_age_ratio),
            category='demographics',
            description='Score based on optimal spending age (40 is peak)',
            is_higher_better=True
        )
        
        # Income per Traffic (quality of customer base)
        income_per_traffic = (
            median_income / (total_traffic / 1000) 
            if total_traffic > 0 else median_income
        )
        # Normalize to 0-100 range
        income_per_traffic_normalized = min(income_per_traffic / 10, 100)
        result.metrics['income_per_traffic'] = DerivedMetric(
            name='Income per Traffic',
            raw_value=income_per_traffic,
            normalized_value=self._normalize('income_per_traffic', income_per_traffic_normalized),
            category='demographics',
            description='Customer quality indicator (income vs traffic volume)',
            is_higher_better=True
        )
        
        # Calculate category scores
        result.category_scores = self._calculate_category_scores(result.metrics)
        
        # Calculate overall score
        result.overall_score = sum(
            score * self.CATEGORY_WEIGHTS.get(category, 0)
            for category, score in result.category_scores.items()
        )
        
        return result
    
    def _normalize(self, metric_key: str, value: float) -> float:
        """Normalize a value to 0-100 scale based on defined ranges"""
        if metric_key not in self.NORMALIZATION_RANGES:
            return min(max(value, 0), 100)
        
        min_val, max_val, is_higher_better = self.NORMALIZATION_RANGES[metric_key]
        
        # Clamp value to range
        clamped = max(min_val, min(value, max_val))
        
        # Calculate normalized score
        if max_val == min_val:
            normalized = 50.0
        else:
            normalized = (clamped - min_val) / (max_val - min_val) * 100
        
        # Invert if lower is better
        if not is_higher_better:
            normalized = 100 - normalized
        
        # Final clamp to ensure 0-100
        return max(0.0, min(100.0, normalized))
    
    def _calculate_category_scores(
        self, 
        metrics: Dict[str, DerivedMetric]
    ) -> Dict[str, float]:
        """Calculate average normalized score for each category"""
        categories: Dict[str, List[float]] = {}
        
        for metric in metrics.values():
            if metric.category not in categories:
                categories[metric.category] = []
            categories[metric.category].append(metric.normalized_value)
        
        return {
            category: sum(scores) / len(scores) if scores else 0
            for category, scores in categories.items()
        }


def calculate_derived_metrics(
    total_population: int,
    population_growth: float,
    median_income: int,
    median_age: float,
    total_competitors: int,
    foot_traffic_monthly: int,
    drive_by_traffic_monthly: int
) -> DerivedMetricsResult:
    """Convenience function to calculate derived metrics"""
    calculator = DerivedMetricsCalculator()
    return calculator.calculate(
        total_population=total_population,
        population_growth=population_growth,
        median_income=median_income,
        median_age=median_age,
        total_competitors=total_competitors,
        foot_traffic_monthly=foot_traffic_monthly,
        drive_by_traffic_monthly=drive_by_traffic_monthly
    )
