"""
Report Pricing Configuration
Defines pricing for all Consultant Studio reports and bundles
"""

from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass


class ReportProductType(str, Enum):
    FEASIBILITY_STUDY = "feasibility_study"
    BUSINESS_PLAN = "business_plan"
    FINANCIAL_MODEL = "financial_model"
    MARKET_ANALYSIS = "market_analysis"
    STRATEGIC_ASSESSMENT = "strategic_assessment"
    PESTLE_ANALYSIS = "pestle_analysis"
    PITCH_DECK = "pitch_deck"


class BundleType(str, Enum):
    STARTER = "starter"
    PROFESSIONAL = "professional"
    CONSULTANT_LICENSE = "consultant_license"


@dataclass
class ReportProduct:
    id: str
    name: str
    description: str
    price_cents: int
    included_in_tier: Optional[str]  # "pro", "business", or None (pay-only)


@dataclass
class Bundle:
    id: str
    name: str
    description: str
    price_cents: int
    reports: List[str]
    savings_cents: int
    is_annual: bool = False
    max_opportunities: Optional[int] = None


REPORT_PRODUCTS: Dict[str, ReportProduct] = {
    ReportProductType.FEASIBILITY_STUDY.value: ReportProduct(
        id=ReportProductType.FEASIBILITY_STUDY.value,
        name="Feasibility Study",
        description="Quick viability check with market validation",
        price_cents=0,
        included_in_tier=None,
    ),
    ReportProductType.PITCH_DECK.value: ReportProduct(
        id=ReportProductType.PITCH_DECK.value,
        name="Pitch Deck Assistant",
        description="Investor presentation outline and key slides",
        price_cents=7900,
        included_in_tier="pro",
    ),
    ReportProductType.PESTLE_ANALYSIS.value: ReportProduct(
        id=ReportProductType.PESTLE_ANALYSIS.value,
        name="PESTLE Analysis",
        description="Political, Economic, Social, Technological, Legal, Environmental factors",
        price_cents=7900,
        included_in_tier="business",
    ),
    ReportProductType.STRATEGIC_ASSESSMENT.value: ReportProduct(
        id=ReportProductType.STRATEGIC_ASSESSMENT.value,
        name="Strategic Assessment",
        description="SWOT analysis and strategic positioning",
        price_cents=8900,
        included_in_tier="pro",
    ),
    ReportProductType.MARKET_ANALYSIS.value: ReportProduct(
        id=ReportProductType.MARKET_ANALYSIS.value,
        name="Market Analysis",
        description="TAM/SAM/SOM with competitive landscape",
        price_cents=9900,
        included_in_tier="business",
    ),
    ReportProductType.FINANCIAL_MODEL.value: ReportProduct(
        id=ReportProductType.FINANCIAL_MODEL.value,
        name="Financial Model",
        description="5-year projections and unit economics",
        price_cents=12900,
        included_in_tier="pro",
    ),
    ReportProductType.BUSINESS_PLAN.value: ReportProduct(
        id=ReportProductType.BUSINESS_PLAN.value,
        name="Business Plan",
        description="Comprehensive strategy document",
        price_cents=14900,
        included_in_tier="pro",
    ),
}

BUNDLES: Dict[str, Bundle] = {
    BundleType.STARTER.value: Bundle(
        id=BundleType.STARTER.value,
        name="Starter Bundle",
        description="Validation + Pitch package for fundraising",
        price_cents=32900,
        reports=[
            ReportProductType.FEASIBILITY_STUDY.value,
            ReportProductType.BUSINESS_PLAN.value,
            ReportProductType.FINANCIAL_MODEL.value,
            ReportProductType.PITCH_DECK.value,
        ],
        savings_cents=2800,
    ),
    BundleType.PROFESSIONAL.value: Bundle(
        id=BundleType.PROFESSIONAL.value,
        name="Professional Bundle",
        description="Complete execution package - replaces consultants",
        price_cents=49900,
        reports=[
            ReportProductType.FEASIBILITY_STUDY.value,
            ReportProductType.BUSINESS_PLAN.value,
            ReportProductType.FINANCIAL_MODEL.value,
            ReportProductType.PITCH_DECK.value,
            ReportProductType.MARKET_ANALYSIS.value,
            ReportProductType.STRATEGIC_ASSESSMENT.value,
            ReportProductType.PESTLE_ANALYSIS.value,
        ],
        savings_cents=12500,
    ),
    BundleType.CONSULTANT_LICENSE.value: Bundle(
        id=BundleType.CONSULTANT_LICENSE.value,
        name="Consultant License",
        description="Unlimited reports for 25 opportunities per year",
        price_cents=249900,
        reports=[
            ReportProductType.FEASIBILITY_STUDY.value,
            ReportProductType.BUSINESS_PLAN.value,
            ReportProductType.FINANCIAL_MODEL.value,
            ReportProductType.PITCH_DECK.value,
            ReportProductType.MARKET_ANALYSIS.value,
            ReportProductType.STRATEGIC_ASSESSMENT.value,
            ReportProductType.PESTLE_ANALYSIS.value,
        ],
        savings_cents=1250000,
        is_annual=True,
        max_opportunities=25,
    ),
}


def get_report_price(report_type: str) -> int:
    product = REPORT_PRODUCTS.get(report_type)
    return product.price_cents if product else 0


def get_bundle_price(bundle_type: str) -> int:
    bundle = BUNDLES.get(bundle_type)
    return bundle.price_cents if bundle else 0


def calculate_bundle_total(report_types: List[str]) -> int:
    total = 0
    for rt in report_types:
        total += get_report_price(rt)
    return total


def is_report_included_for_tier(report_type: str, user_tier: str) -> bool:
    product = REPORT_PRODUCTS.get(report_type)
    if not product or not product.included_in_tier:
        return False
    
    tier_order = ["free", "pro", "business", "enterprise"]
    try:
        user_tier_idx = tier_order.index(user_tier.lower())
        included_tier_idx = tier_order.index(product.included_in_tier.lower())
        return user_tier_idx >= included_tier_idx
    except ValueError:
        return False


def get_pricing_summary() -> dict:
    return {
        "reports": [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "price": p.price_cents,
                "included_in_tier": p.included_in_tier,
            }
            for p in REPORT_PRODUCTS.values()
        ],
        "bundles": [
            {
                "id": b.id,
                "name": b.name,
                "description": b.description,
                "price": b.price_cents,
                "reports": b.reports,
                "savings": b.savings_cents,
                "is_annual": b.is_annual,
                "max_opportunities": b.max_opportunities,
            }
            for b in BUNDLES.values()
        ],
    }
