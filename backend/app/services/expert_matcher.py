"""
Expert Matcher Service

Matches experts to opportunities using a weighted scoring algorithm.
Considers: category alignment, skill overlap, success metrics, availability.
"""

import json
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.expert import Expert
from app.models.opportunity import Opportunity

logger = logging.getLogger(__name__)

CATEGORY_WEIGHT = 0.35
SKILL_WEIGHT = 0.30
SUCCESS_WEIGHT = 0.20
AVAILABILITY_WEIGHT = 0.10
RATING_WEIGHT = 0.05

CATEGORY_SKILL_MAP = {
    "Technology & Software": ["software development", "saas", "api", "mobile apps", "ai/ml", "cloud computing"],
    "Healthcare": ["healthtech", "medical devices", "telemedicine", "patient care", "health insurance"],
    "Food & Dining": ["restaurant", "food service", "delivery", "culinary", "hospitality"],
    "Real Estate": ["property management", "real estate investing", "construction", "architecture"],
    "Transportation": ["logistics", "fleet management", "ride sharing", "supply chain"],
    "Education": ["edtech", "curriculum design", "e-learning", "tutoring", "training"],
    "Finance & Banking": ["fintech", "banking", "payments", "lending", "wealth management"],
    "Retail & E-commerce": ["e-commerce", "retail operations", "inventory", "merchandising"],
    "Money & Finance": ["fintech", "payments", "budgeting", "invoicing", "accounting"],
    "Home Services": ["home improvement", "cleaning", "maintenance", "landscaping"],
    "Childcare": ["childcare", "education", "family services", "parenting"],
    "Entertainment": ["media", "gaming", "streaming", "content creation"],
}


def parse_json_field(field_value: Optional[str]) -> List[str]:
    """Safely parse a JSON text field to a list."""
    if not field_value:
        return []
    try:
        result = json.loads(field_value)
        if isinstance(result, list):
            return [str(item).lower() for item in result]
        return []
    except (json.JSONDecodeError, TypeError):
        return []


def calculate_category_score(expert: Expert, opportunity: Opportunity) -> float:
    """Calculate category alignment score (0-1)."""
    expert_categories = parse_json_field(expert.categories)
    opp_category = (opportunity.category or "").lower()
    opp_subcategory = (opportunity.subcategory or "").lower()
    
    if not expert_categories:
        return 0.3
    
    for cat in expert_categories:
        if cat == opp_category or cat in opp_category or opp_category in cat:
            return 1.0
        if opp_subcategory and (cat == opp_subcategory or cat in opp_subcategory):
            return 0.8
    
    return 0.2


def calculate_skill_score(expert: Expert, opportunity: Opportunity) -> float:
    """Calculate skill overlap score (0-1)."""
    expert_skills = parse_json_field(expert.skills)
    expert_specs = parse_json_field(expert.specialization)
    all_expert_skills = set(expert_skills + expert_specs)
    
    if not all_expert_skills:
        return 0.3
    
    opp_category = (opportunity.category or "").lower()
    relevant_skills = CATEGORY_SKILL_MAP.get(opportunity.category, [])
    
    opp_title = (opportunity.title or "").lower()
    opp_desc = (opportunity.description or "").lower()
    opp_text = f"{opp_title} {opp_desc}"
    
    matches = 0
    for skill in all_expert_skills:
        if skill in opp_text or any(rs in skill for rs in relevant_skills):
            matches += 1
    
    if matches == 0:
        return 0.2
    
    score = min(1.0, matches / 3)
    return score


def calculate_success_score(expert: Expert) -> float:
    """Calculate success metrics score (0-1)."""
    success_rate = float(expert.success_rate or 0)
    completed = expert.completed_projects or 0
    
    rate_score = min(1.0, success_rate / 100)
    project_score = min(1.0, completed / 50)
    
    return (rate_score * 0.6) + (project_score * 0.4)


def calculate_availability_score(expert: Expert) -> float:
    """Calculate availability score (0-1)."""
    if not expert.is_active:
        return 0.0
    if not expert.is_available:
        return 0.3
    return 1.0


def calculate_rating_score(expert: Expert) -> float:
    """Calculate rating score (0-1)."""
    rating = expert.avg_rating or 0
    reviews = expert.total_reviews or 0
    
    if reviews < 3:
        return 0.5
    
    return min(1.0, rating / 5.0)


def calculate_match_score(expert: Expert, opportunity: Opportunity) -> float:
    """
    Calculate weighted match score for an expert-opportunity pair.
    
    Weights:
    - Category alignment: 35%
    - Skill overlap: 30%
    - Success metrics: 20%
    - Availability: 10%
    - Rating: 5%
    """
    category_score = calculate_category_score(expert, opportunity)
    skill_score = calculate_skill_score(expert, opportunity)
    success_score = calculate_success_score(expert)
    availability_score = calculate_availability_score(expert)
    rating_score = calculate_rating_score(expert)
    
    total_score = (
        (category_score * CATEGORY_WEIGHT) +
        (skill_score * SKILL_WEIGHT) +
        (success_score * SUCCESS_WEIGHT) +
        (availability_score * AVAILABILITY_WEIGHT) +
        (rating_score * RATING_WEIGHT)
    )
    
    return round(total_score * 100, 1)


def get_recommended_experts(
    db: Session,
    opportunity_id: int,
    limit: int = 5,
    min_score: float = 30.0
) -> List[dict]:
    """
    Get recommended experts for an opportunity.
    
    Returns a list of expert dicts with match scores, sorted by relevance.
    """
    opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opportunity:
        logger.warning(f"Opportunity {opportunity_id} not found")
        return []
    
    experts = db.query(Expert).filter(Expert.is_active == True).all()
    
    scored_experts = []
    for expert in experts:
        score = calculate_match_score(expert, opportunity)
        if score >= min_score:
            scored_experts.append({
                "id": expert.id,
                "name": expert.name,
                "headline": expert.headline,
                "avatar_url": expert.avatar_url,
                "skills": parse_json_field(expert.skills),
                "specialization": parse_json_field(expert.specialization),
                "categories": parse_json_field(expert.categories),
                "avg_rating": float(expert.avg_rating) if expert.avg_rating else None,
                "total_reviews": expert.total_reviews or 0,
                "completed_projects": expert.completed_projects or 0,
                "success_rate": float(expert.success_rate) if expert.success_rate else None,
                "is_available": expert.is_available,
                "hourly_rate_cents": expert.hourly_rate_cents,
                "pricing_model": expert.pricing_model.value if expert.pricing_model else None,
                "match_score": score,
                "match_reason": get_match_reason(expert, opportunity, score)
            })
    
    scored_experts.sort(key=lambda x: x["match_score"], reverse=True)
    
    return scored_experts[:limit]


def get_match_reason(expert: Expert, opportunity: Opportunity, score: float) -> str:
    """Generate a human-readable reason for the match."""
    reasons = []
    
    expert_categories = parse_json_field(expert.categories)
    opp_category = (opportunity.category or "").lower()
    for cat in expert_categories:
        if cat == opp_category or cat in opp_category:
            reasons.append(f"Specializes in {opportunity.category}")
            break
    
    if expert.completed_projects and expert.completed_projects > 20:
        reasons.append(f"{expert.completed_projects} completed projects")
    
    if expert.avg_rating and expert.avg_rating >= 4.5:
        reasons.append(f"{expert.avg_rating:.1f} rating")
    
    if not reasons:
        if score >= 70:
            reasons.append("Strong skill match")
        elif score >= 50:
            reasons.append("Good fit for this opportunity")
        else:
            reasons.append("Available expert")
    
    return " • ".join(reasons[:2])


def seed_demo_experts(db: Session) -> None:
    """Seed database with demo experts for testing."""
    existing = db.query(Expert).count()
    if existing > 0:
        logger.info(f"Found {existing} experts, skipping seed")
        return
    
    demo_experts = [
        {
            "name": "Sarah Chen",
            "headline": "Market Strategy Consultant",
            "bio": "15+ years helping startups validate and enter new markets",
            "skills": json.dumps(["market research", "go-to-market strategy", "competitive analysis", "pricing strategy"]),
            "specialization": json.dumps(["B2B SaaS", "marketplace", "fintech"]),
            "categories": json.dumps(["Technology & Software", "Money & Finance", "Retail & E-commerce"]),
            "success_rate": 94.5,
            "avg_rating": 4.9,
            "total_reviews": 47,
            "completed_projects": 47,
            "is_active": True,
            "is_available": True,
            "hourly_rate_cents": 25000,
            "pricing_model": "hourly",
        },
        {
            "name": "Michael Torres",
            "headline": "Industry Analyst",
            "bio": "Former McKinsey consultant specializing in market sizing and competitive intelligence",
            "skills": json.dumps(["market sizing", "industry analysis", "financial modeling", "due diligence"]),
            "specialization": json.dumps(["healthcare", "real estate", "transportation"]),
            "categories": json.dumps(["Healthcare", "Real Estate", "Transportation"]),
            "success_rate": 91.0,
            "avg_rating": 4.8,
            "total_reviews": 32,
            "completed_projects": 32,
            "is_active": True,
            "is_available": True,
            "hourly_rate_cents": 30000,
            "pricing_model": "hourly",
        },
        {
            "name": "Emily Park",
            "headline": "Business Development Expert",
            "bio": "Scaled 3 startups from 0 to $10M+ ARR",
            "skills": json.dumps(["growth strategy", "partnership development", "sales strategy", "fundraising"]),
            "specialization": json.dumps(["edtech", "consumer apps", "subscription models"]),
            "categories": json.dumps(["Education", "Technology & Software", "Entertainment"]),
            "success_rate": 88.0,
            "avg_rating": 4.7,
            "total_reviews": 28,
            "completed_projects": 28,
            "is_active": True,
            "is_available": True,
            "hourly_rate_cents": 22000,
            "pricing_model": "hourly",
        },
        {
            "name": "David Kim",
            "headline": "Operations & Logistics Consultant",
            "bio": "Supply chain expert with experience at Amazon and Uber",
            "skills": json.dumps(["supply chain", "logistics optimization", "operations management", "process automation"]),
            "specialization": json.dumps(["last-mile delivery", "warehouse operations", "fleet management"]),
            "categories": json.dumps(["Transportation", "Food & Dining", "Retail & E-commerce"]),
            "success_rate": 92.0,
            "avg_rating": 4.8,
            "total_reviews": 41,
            "completed_projects": 41,
            "is_active": True,
            "is_available": True,
            "hourly_rate_cents": 27500,
            "pricing_model": "hourly",
        },
        {
            "name": "Jennifer Walsh",
            "headline": "Product Strategy Lead",
            "bio": "Ex-Google PM helping founders build products users love",
            "skills": json.dumps(["product management", "user research", "roadmap planning", "agile methodology"]),
            "specialization": json.dumps(["consumer products", "mobile apps", "AI/ML products"]),
            "categories": json.dumps(["Technology & Software", "Healthcare", "Education"]),
            "success_rate": 96.0,
            "avg_rating": 4.9,
            "total_reviews": 55,
            "completed_projects": 55,
            "is_active": True,
            "is_available": False,
            "hourly_rate_cents": 35000,
            "pricing_model": "hourly",
        },
    ]
    
    from app.models.expert import ExpertPricingModel
    
    for expert_data in demo_experts:
        pricing = expert_data.pop("pricing_model")
        expert = Expert(
            **expert_data,
            pricing_model=ExpertPricingModel(pricing)
        )
        db.add(expert)
    
    db.commit()
    logger.info(f"Seeded {len(demo_experts)} demo experts")
