"""
Seed script to populate the expert marketplace with real or sample expert data.

Tries to use Upwork API if configured, otherwise uses curated sample data
based on realistic expert profiles.
"""

import asyncio
import os
import sys
import json
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.expert_collaboration import ExpertProfile, ExpertCategory
from app.services.upwork_service import UpworkService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CATEGORY_SEARCH_TERMS = [
    {"query": "business strategy consultant", "category": ExpertCategory.STRATEGY_CONSULTANT, "upwork_category": "531770282580668429"},
    {"query": "market research analyst", "category": ExpertCategory.MARKET_RESEARCHER, "upwork_category": "531770282580668425"},
    {"query": "startup legal advisor", "category": ExpertCategory.LEGAL_ADVISOR, "upwork_category": "531770282580668428"},
    {"query": "financial consultant CFO", "category": ExpertCategory.FINANCIAL_ADVISOR, "upwork_category": "531770282580668429"},
    {"query": "software architect", "category": ExpertCategory.TECHNICAL_ADVISOR, "upwork_category": "531770282580668418"},
    {"query": "digital marketing strategist", "category": ExpertCategory.MARKETING_SPECIALIST, "upwork_category": "531770282580668422"},
    {"query": "product manager", "category": ExpertCategory.PRODUCT_STRATEGIST, "upwork_category": "531770282580668418"},
    {"query": "sales consultant B2B", "category": ExpertCategory.SALES_ADVISOR, "upwork_category": "531770282580668431"},
    {"query": "operations consultant", "category": ExpertCategory.OPERATIONS_EXPERT, "upwork_category": "531770282580668429"},
    {"query": "data scientist analytics", "category": ExpertCategory.DATA_ANALYST, "upwork_category": "531770282580668425"},
]

SAMPLE_EXPERTS = [
    {
        "name": "Sarah Chen",
        "title": "Strategic Business Consultant | Former McKinsey",
        "bio": "15+ years helping startups and Fortune 500 companies develop winning strategies. Specializing in market entry, growth strategies, and operational excellence. Former McKinsey engagement manager with deep expertise in tech and consumer sectors.",
        "hourly_rate": 250,
        "skills": ["Business Strategy", "Market Analysis", "Growth Planning", "M&A Advisory", "Due Diligence"],
        "location": "San Francisco, CA",
        "category": ExpertCategory.STRATEGY_CONSULTANT,
        "avg_rating": 4.9,
        "projects_completed": 47,
        "avatar_url": None
    },
    {
        "name": "Michael Rodriguez",
        "title": "Market Research & Consumer Insights Expert",
        "bio": "Former Director of Consumer Insights at Nielsen. I help companies understand their markets through rigorous research, competitive analysis, and data-driven insights. Expertise in survey design, focus groups, and market sizing.",
        "hourly_rate": 175,
        "skills": ["Market Research", "Consumer Insights", "Competitive Analysis", "Survey Design", "Data Analysis"],
        "location": "New York, NY",
        "category": ExpertCategory.MARKET_RESEARCHER,
        "avg_rating": 4.8,
        "projects_completed": 63,
        "avatar_url": None
    },
    {
        "name": "Jennifer Park",
        "title": "Startup Attorney | VC & Fundraising Specialist",
        "bio": "Partner at a top Silicon Valley law firm specializing in startup law. I've helped 200+ startups with incorporation, fundraising, IP protection, and exits. Expert in SAFE notes, term sheets, and regulatory compliance.",
        "hourly_rate": 350,
        "skills": ["Startup Law", "Fundraising", "IP Protection", "Corporate Governance", "M&A"],
        "location": "Palo Alto, CA",
        "category": ExpertCategory.LEGAL_ADVISOR,
        "avg_rating": 5.0,
        "projects_completed": 89,
        "avatar_url": None
    },
    {
        "name": "David Thompson",
        "title": "CFO-as-a-Service | Startup Financial Strategy",
        "bio": "Former CFO of 3 successful startups (2 exits). I provide fractional CFO services including financial modeling, fundraising support, unit economics optimization, and investor relations. CPA with MBA from Wharton.",
        "hourly_rate": 275,
        "skills": ["Financial Modeling", "Fundraising", "Unit Economics", "Budgeting", "Investor Relations"],
        "location": "Boston, MA",
        "category": ExpertCategory.FINANCIAL_ADVISOR,
        "avg_rating": 4.9,
        "projects_completed": 52,
        "avatar_url": None
    },
    {
        "name": "Alex Kumar",
        "title": "Technical Architect | Ex-Google Staff Engineer",
        "bio": "20+ years building scalable systems at Google, Amazon, and startups. I help founders make critical technology decisions, architect systems for scale, and build high-performing engineering teams. Expert in cloud architecture and AI/ML.",
        "hourly_rate": 300,
        "skills": ["System Architecture", "Cloud Infrastructure", "AI/ML", "Technical Leadership", "Code Review"],
        "location": "Seattle, WA",
        "category": ExpertCategory.TECHNICAL_ADVISOR,
        "avg_rating": 4.9,
        "projects_completed": 71,
        "avatar_url": None
    },
    {
        "name": "Emma Williams",
        "title": "Growth Marketing Expert | $500M+ Revenue Generated",
        "bio": "Former VP Marketing at two unicorn startups. I specialize in building marketing engines that drive sustainable growth. Expertise in paid acquisition, content marketing, brand strategy, and marketing analytics.",
        "hourly_rate": 225,
        "skills": ["Growth Marketing", "Paid Acquisition", "Content Strategy", "Brand Building", "Analytics"],
        "location": "Austin, TX",
        "category": ExpertCategory.MARKETING_SPECIALIST,
        "avg_rating": 4.8,
        "projects_completed": 58,
        "avatar_url": None
    },
    {
        "name": "Ryan Foster",
        "title": "Product Leader | Built Products Used by 100M+ Users",
        "bio": "Former Director of Product at Spotify and Meta. I help startups define product vision, build product roadmaps, and create products users love. Expert in product-market fit, user research, and agile development.",
        "hourly_rate": 250,
        "skills": ["Product Strategy", "User Research", "Roadmapping", "Product-Market Fit", "Agile"],
        "location": "Los Angeles, CA",
        "category": ExpertCategory.PRODUCT_STRATEGIST,
        "avg_rating": 4.9,
        "projects_completed": 44,
        "avatar_url": None
    },
    {
        "name": "Lisa Martinez",
        "title": "B2B Sales Expert | $200M+ Pipeline Built",
        "bio": "Former VP Sales at Salesforce and Oracle. I help startups build sales processes, train teams, and close enterprise deals. Expertise in consultative selling, sales enablement, and building scalable sales organizations.",
        "hourly_rate": 200,
        "skills": ["B2B Sales", "Enterprise Sales", "Sales Process", "Team Training", "Pipeline Development"],
        "location": "Chicago, IL",
        "category": ExpertCategory.SALES_ADVISOR,
        "avg_rating": 4.7,
        "projects_completed": 39,
        "avatar_url": None
    },
    {
        "name": "James Wilson",
        "title": "Operations & Supply Chain Expert | Ex-Amazon",
        "bio": "Former Director of Operations at Amazon. I help companies optimize their operations, build efficient supply chains, and scale their fulfillment. Expert in logistics, inventory management, and process optimization.",
        "hourly_rate": 225,
        "skills": ["Operations Management", "Supply Chain", "Process Optimization", "Logistics", "Inventory Management"],
        "location": "Denver, CO",
        "category": ExpertCategory.OPERATIONS_EXPERT,
        "avg_rating": 4.8,
        "projects_completed": 33,
        "avatar_url": None
    },
    {
        "name": "Priya Patel",
        "title": "Data Scientist | ML/AI Strategy for Startups",
        "bio": "Former Senior Data Scientist at Netflix and Uber. I help startups leverage data and AI to build competitive advantages. Expert in predictive analytics, recommendation systems, and data infrastructure.",
        "hourly_rate": 275,
        "skills": ["Data Science", "Machine Learning", "Analytics", "Python", "Data Strategy"],
        "location": "San Jose, CA",
        "category": ExpertCategory.DATA_ANALYST,
        "avg_rating": 4.9,
        "projects_completed": 41,
        "avatar_url": None
    },
    {
        "name": "Thomas Anderson",
        "title": "UX/UI Design Leader | Human-Centered Design",
        "bio": "Former Head of Design at Airbnb. I help startups create exceptional user experiences through research-driven design. Expert in design systems, user testing, and building design teams.",
        "hourly_rate": 200,
        "skills": ["UX Design", "UI Design", "Design Systems", "User Research", "Prototyping"],
        "location": "Portland, OR",
        "category": ExpertCategory.TECHNICAL_ADVISOR,
        "avg_rating": 4.8,
        "projects_completed": 56,
        "avatar_url": None
    },
    {
        "name": "Rachel Kim",
        "title": "Fundraising Expert | $2B+ Raised for Clients",
        "bio": "Former VC partner turned fundraising advisor. I help founders craft compelling narratives, prepare pitch materials, and navigate the fundraising process. Expertise from seed to Series C rounds.",
        "hourly_rate": 350,
        "skills": ["Fundraising", "Pitch Decks", "Investor Relations", "Valuation", "Term Sheets"],
        "location": "Menlo Park, CA",
        "category": ExpertCategory.FINANCIAL_ADVISOR,
        "avg_rating": 5.0,
        "projects_completed": 67,
        "avatar_url": None
    },
    {
        "name": "Marcus Johnson",
        "title": "E-commerce & DTC Growth Expert",
        "bio": "Scaled 3 DTC brands to $50M+ revenue. I specialize in e-commerce strategy, customer acquisition, retention, and unit economics. Expert in Shopify, subscription models, and omnichannel retail.",
        "hourly_rate": 200,
        "skills": ["E-commerce", "DTC Strategy", "Customer Acquisition", "Retention", "Shopify"],
        "location": "Miami, FL",
        "category": ExpertCategory.MARKETING_SPECIALIST,
        "avg_rating": 4.7,
        "projects_completed": 48,
        "avatar_url": None
    },
    {
        "name": "Amanda Chen",
        "title": "HR & Talent Strategy for High-Growth Startups",
        "bio": "Former VP People at Stripe. I help startups build exceptional teams and culture. Expertise in talent acquisition, compensation strategy, org design, and scaling from 10 to 500+ employees.",
        "hourly_rate": 225,
        "skills": ["Talent Strategy", "HR", "Compensation", "Culture Building", "Org Design"],
        "location": "New York, NY",
        "category": ExpertCategory.OPERATIONS_EXPERT,
        "avg_rating": 4.9,
        "projects_completed": 35,
        "avatar_url": None
    },
    {
        "name": "Robert Lee",
        "title": "Healthcare & Biotech Regulatory Expert",
        "bio": "Former FDA reviewer and biotech executive. I help healthcare startups navigate regulatory pathways, clinical trials, and market access. Expert in FDA 510(k), PMA, and digital health regulations.",
        "hourly_rate": 400,
        "skills": ["FDA Regulations", "Clinical Trials", "Healthcare Compliance", "Medical Devices", "Biotech"],
        "location": "Washington, DC",
        "category": ExpertCategory.LEGAL_ADVISOR,
        "avg_rating": 4.9,
        "projects_completed": 29,
        "avatar_url": None
    },
    {
        "name": "Sofia Ramirez",
        "title": "Brand Strategy & Creative Director",
        "bio": "Former Creative Director at IDEO. I help startups build memorable brands that resonate with customers. Expertise in brand positioning, visual identity, storytelling, and launch campaigns.",
        "hourly_rate": 225,
        "skills": ["Brand Strategy", "Creative Direction", "Visual Identity", "Storytelling", "Launch Campaigns"],
        "location": "Brooklyn, NY",
        "category": ExpertCategory.MARKETING_SPECIALIST,
        "avg_rating": 4.8,
        "projects_completed": 42,
        "avatar_url": None
    },
    {
        "name": "Christopher Wright",
        "title": "Cybersecurity & Compliance Expert",
        "bio": "Former CISO at a Fortune 100 company. I help startups build secure systems and achieve compliance (SOC 2, HIPAA, GDPR). Expert in security architecture, penetration testing, and risk management.",
        "hourly_rate": 300,
        "skills": ["Cybersecurity", "SOC 2", "HIPAA", "GDPR", "Security Architecture"],
        "location": "Reston, VA",
        "category": ExpertCategory.TECHNICAL_ADVISOR,
        "avg_rating": 4.9,
        "projects_completed": 37,
        "avatar_url": None
    },
    {
        "name": "Michelle Zhang",
        "title": "International Expansion & GTM Strategy",
        "bio": "Led international expansion at 3 tech companies across Asia and Europe. I help startups navigate global markets, localization, and cross-border operations. Fluent in Mandarin, Japanese, and Spanish.",
        "hourly_rate": 250,
        "skills": ["International Expansion", "Go-to-Market", "Localization", "Cross-border Operations", "Market Entry"],
        "location": "San Francisco, CA",
        "category": ExpertCategory.STRATEGY_CONSULTANT,
        "avg_rating": 4.8,
        "projects_completed": 31,
        "avatar_url": None
    },
    {
        "name": "Daniel Brown",
        "title": "SaaS Metrics & Pricing Strategy Expert",
        "bio": "Former VP Strategy at a $1B SaaS company. I help startups optimize pricing, reduce churn, and improve unit economics. Expert in subscription models, pricing psychology, and revenue optimization.",
        "hourly_rate": 275,
        "skills": ["SaaS Metrics", "Pricing Strategy", "Churn Reduction", "Revenue Optimization", "Subscription Models"],
        "location": "Salt Lake City, UT",
        "category": ExpertCategory.STRATEGY_CONSULTANT,
        "avg_rating": 4.9,
        "projects_completed": 45,
        "avatar_url": None
    },
    {
        "name": "Katherine O'Connor",
        "title": "PR & Communications Expert | Crisis Management",
        "bio": "Former Communications Director at a major tech company. I help startups build media relationships, craft press strategies, and manage communications during critical moments. Expert in thought leadership and crisis PR.",
        "hourly_rate": 200,
        "skills": ["Public Relations", "Communications", "Media Strategy", "Crisis Management", "Thought Leadership"],
        "location": "Philadelphia, PA",
        "category": ExpertCategory.MARKETING_SPECIALIST,
        "avg_rating": 4.7,
        "projects_completed": 53,
        "avatar_url": None
    },
]


async def try_import_from_upwork(db: Session) -> int:
    """Try to import experts from Upwork API."""
    imported_count = 0
    
    for search in CATEGORY_SEARCH_TERMS:
        logger.info(f"Searching Upwork for: {search['query']}")
        
        result = await UpworkService.search_freelancers(
            query=search['query'],
            job_success_min=90,
            limit=5
        )
        
        if result.get("error"):
            logger.warning(f"Upwork API error: {result['error']}")
            continue
        
        freelancers = result.get("freelancers", [])
        logger.info(f"Found {len(freelancers)} freelancers")
        
        for f in freelancers:
            existing = db.query(ExpertProfile).filter(
                ExpertProfile.external_id == f["id"],
                ExpertProfile.external_source == "upwork"
            ).first()
            
            if existing:
                continue
            
            expert_profile = ExpertProfile(
                user_id=None,
                title=f.get("title", ""),
                bio=f.get("description", ""),
                hourly_rate_cents=int(f["hourly_rate"] * 100) if f.get("hourly_rate") else None,
                skills=json.dumps(f.get("skills", [])) if f.get("skills") else None,
                location=f"{f.get('city', '')}, {f.get('country', '')}".strip(", ") if f.get("country") else None,
                avatar_url=f.get("avatar_url"),
                avg_rating=f.get("avg_rating"),
                total_reviews=0,
                projects_completed=f.get("total_jobs", 0),
                is_verified=True,
                is_available=True,
                external_id=f["id"],
                external_source="upwork",
                external_url=f.get("profile_url"),
                external_name=f.get("name", ""),
                category=search["category"]
            )
            db.add(expert_profile)
            imported_count += 1
        
        db.commit()
    
    return imported_count


def seed_sample_experts(db: Session) -> int:
    """Seed with curated sample expert data."""
    imported_count = 0
    
    for expert_data in SAMPLE_EXPERTS:
        existing = db.query(ExpertProfile).filter(
            ExpertProfile.external_name == expert_data["name"],
            ExpertProfile.external_source == "sample"
        ).first()
        
        if existing:
            logger.info(f"Skipping existing expert: {expert_data['name']}")
            continue
        
        expert_profile = ExpertProfile(
            user_id=None,
            title=expert_data["title"],
            bio=expert_data["bio"],
            hourly_rate_cents=expert_data["hourly_rate"] * 100,
            skills=json.dumps(expert_data["skills"]),
            location=expert_data["location"],
            avatar_url=expert_data.get("avatar_url"),
            avg_rating=expert_data["avg_rating"],
            total_reviews=int(expert_data["projects_completed"] * 0.7),
            projects_completed=expert_data["projects_completed"],
            is_verified=True,
            is_available=True,
            external_id=f"sample_{expert_data['name'].lower().replace(' ', '_')}",
            external_source="sample",
            external_url=None,
            external_name=expert_data["name"],
            category=expert_data["category"]
        )
        db.add(expert_profile)
        imported_count += 1
        logger.info(f"Added expert: {expert_data['name']} ({expert_data['category'].value})")
    
    db.commit()
    return imported_count


async def main():
    db = SessionLocal()
    
    try:
        logger.info("=== Expert Seeding Script ===")
        
        upwork_api_key = os.getenv("UPWORK_API_KEY", "")
        upwork_api_secret = os.getenv("UPWORK_API_SECRET", "")
        
        if upwork_api_key and upwork_api_secret:
            logger.info("Upwork API credentials found. Attempting to import real freelancers...")
            upwork_count = await try_import_from_upwork(db)
            logger.info(f"Imported {upwork_count} experts from Upwork")
            
            if upwork_count < 10:
                logger.info("Supplementing with sample data...")
                sample_count = seed_sample_experts(db)
                logger.info(f"Added {sample_count} sample experts")
        else:
            logger.info("Upwork API not configured. Using curated sample data...")
            sample_count = seed_sample_experts(db)
            logger.info(f"Added {sample_count} sample experts")
        
        total_experts = db.query(ExpertProfile).count()
        logger.info(f"\n=== Seeding Complete ===")
        logger.info(f"Total experts in database: {total_experts}")
        
    except Exception as e:
        logger.error(f"Error during seeding: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
