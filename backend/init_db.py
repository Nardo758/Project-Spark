"""
Initialize the database with sample data
Run this script after starting the database to populate it with test data
"""

import sys
import time
import logging
from app.db.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.opportunity import Opportunity
from app.core.security import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def wait_for_db(max_retries=5, delay=2):
    """Wait for database to be available"""
    from sqlalchemy import text
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting to connect to database (attempt {attempt + 1}/{max_retries})...")
            db = SessionLocal()
            db.execute(text("SELECT 1"))
            db.close()
            logger.info("Database connection successful!")
            return True
        except Exception as e:
            logger.warning(f"Database connection failed: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logger.error("Max retries reached. Database is not available.")
                return False
    return False

def init_db():
    """Initialize database with sample data"""

    # Wait for database to be available
    if not wait_for_db():
        logger.warning("Skipping database initialization - database not available")
        logger.info("Database will be initialized on first API request")
        return

    try:
        # Create tables
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully!")
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        logger.warning("Tables will be created on first API request")
        return

    db = SessionLocal()

    try:
        # Check if we already have data
        existing_users = db.query(User).count()
        if existing_users > 0:
            print("Database already has data. Skipping initialization.")
            return

        # Create sample users
        users = [
            User(
                email="john@example.com",
                name="John Doe",
                bio="Entrepreneur and problem solver",
                hashed_password=get_password_hash("password123"),
                impact_points=150,
                is_verified=True
            ),
            User(
                email="jane@example.com",
                name="Jane Smith",
                bio="Product manager passionate about solving real problems",
                hashed_password=get_password_hash("password123"),
                impact_points=200,
                is_verified=True
            ),
            User(
                email="demo@example.com",
                name="Demo User",
                bio="Demo account for testing",
                hashed_password=get_password_hash("demo123"),
                impact_points=50,
                is_verified=True
            )
        ]

        db.add_all(users)
        db.commit()

        # Refresh to get IDs
        for user in users:
            db.refresh(user)

        # Create sample opportunities with geographic data
        opportunities = [
            # Money & Finance
            Opportunity(
                title="Difficult to track freelance invoices and payments",
                description="As a freelancer, I struggle to keep track of multiple invoices, payment statuses, and client communications. Need a simple solution to manage everything in one place.",
                category="Money & Finance",
                subcategory="Invoicing",
                severity=4,
                validation_count=234,
                growth_rate=15.3,
                market_size="$50M-$100M",
                geographic_scope="online",
                author_id=users[0].id,
                completion_status="open",
                status="active"
            ),
            Opportunity(
                title="Subscription management is a nightmare",
                description="I have too many subscriptions and keep forgetting to cancel trials. Need a centralized way to track and manage all subscriptions.",
                category="Money & Finance",
                subcategory="Personal Finance",
                severity=4,
                validation_count=312,
                growth_rate=22.5,
                market_size="$100M-$500M",
                geographic_scope="online",
                author_id=users[2].id,
                completion_status="in_progress",
                status="active"
            ),
            Opportunity(
                title="Banking apps don't work well for couples managing joint expenses",
                description="My partner and I need better tools to track shared expenses, split bills, and manage our joint financial goals. Current banking apps aren't designed for this.",
                category="Money & Finance",
                subcategory="Personal Finance",
                severity=3,
                validation_count=187,
                growth_rate=16.8,
                market_size="$50M-$100M",
                geographic_scope="online",
                author_id=users[1].id,
                completion_status="open",
                status="active"
            ),
            Opportunity(
                title="Tax preparation is confusing for gig workers",
                description="As someone who does multiple gig jobs, tracking deductions and preparing taxes is overwhelming. Need guidance specific to gig economy workers.",
                category="Money & Finance",
                subcategory="Taxes",
                severity=5,
                validation_count=421,
                growth_rate=28.3,
                market_size="$100M-$500M",
                geographic_scope="national",
                country="United States",
                author_id=users[0].id,
                completion_status="open",
                status="active"
            ),

            # Home & Living
            Opportunity(
                title="Hard to find reliable local handyman services",
                description="Whenever something breaks at home, it's incredibly difficult to find a trustworthy handyman. Most platforms have mixed reviews and unreliable service.",
                category="Home & Living",
                subcategory="Home Services",
                severity=3,
                validation_count=189,
                growth_rate=8.7,
                market_size="$10M-$50M",
                geographic_scope="local",
                country="United States",
                region="California",
                city="San Francisco",
                author_id=users[1].id,
                completion_status="open",
                status="active"
            ),
            Opportunity(
                title="Coordinating furniture delivery windows is frustrating",
                description="I have to take entire days off work for 4-hour delivery windows. Why can't we get real-time tracking like for food delivery?",
                category="Home & Living",
                subcategory="Furniture",
                severity=3,
                validation_count=256,
                growth_rate=11.4,
                market_size="$50M-$100M",
                geographic_scope="national",
                country="United States",
                author_id=users[2].id,
                completion_status="open",
                status="active"
            ),
            Opportunity(
                title="Finding short-term housing between leases is nearly impossible",
                description="When my lease ended before my new one started, I couldn't find affordable month-to-month housing. Hotels are too expensive, Airbnb adds too many fees.",
                category="Home & Living",
                subcategory="Housing",
                severity=4,
                validation_count=298,
                growth_rate=19.2,
                market_size="$100M-$500M",
                geographic_scope="regional",
                country="United States",
                region="New York",
                city="New York",
                author_id=users[0].id,
                completion_status="open",
                status="active"
            ),

            # Health & Wellness
            Opportunity(
                title="Gym equipment often broken or unavailable",
                description="At my gym, popular equipment is always occupied or broken. Would love a system to reserve equipment or see real-time availability.",
                category="Health & Wellness",
                subcategory="Fitness",
                severity=2,
                validation_count=156,
                growth_rate=12.1,
                market_size="$10M-$50M",
                geographic_scope="local",
                country="United States",
                region="New York",
                author_id=users[0].id,
                completion_status="open",
                status="active"
            ),
            Opportunity(
                title="Managing multiple doctor appointments across providers is chaos",
                description="I see multiple specialists and each has their own portal. Keeping track of appointments, medications, and test results is overwhelming.",
                category="Health & Wellness",
                subcategory="Healthcare",
                severity=5,
                validation_count=523,
                growth_rate=24.7,
                market_size="$500M+",
                geographic_scope="national",
                country="United States",
                author_id=None,
                is_anonymous=True,
                completion_status="open",
                status="active"
            ),
            Opportunity(
                title="Healthy meal prep is too time-consuming for busy professionals",
                description="I want to eat healthy but don't have time to meal prep. Current meal delivery services are either unhealthy or too expensive.",
                category="Health & Wellness",
                subcategory="Nutrition",
                severity=3,
                validation_count=367,
                growth_rate=20.1,
                market_size="$100M-$500M",
                geographic_scope="online",
                author_id=users[1].id,
                completion_status="solved",
                status="active"
            ),
            Opportunity(
                title="Finding mental health therapists who accept insurance is difficult",
                description="Spent weeks trying to find a therapist who accepts my insurance, has availability, and specializes in my needs. The process is broken.",
                category="Health & Wellness",
                subcategory="Mental Health",
                severity=5,
                validation_count=612,
                growth_rate=31.5,
                market_size="$500M+",
                geographic_scope="national",
                country="United States",
                author_id=users[2].id,
                completion_status="in_progress",
                status="active"
            ),

            # Transportation
            Opportunity(
                title="Finding parking in the city is extremely stressful",
                description="Spending 20-30 minutes circling blocks looking for parking. Need real-time parking availability for street parking.",
                category="Transportation",
                subcategory="Parking",
                severity=5,
                validation_count=445,
                growth_rate=18.9,
                market_size="$100M-$500M",
                geographic_scope="regional",
                country="United States",
                region="California",
                author_id=None,
                is_anonymous=True,
                completion_status="open",
                status="active"
            ),
            Opportunity(
                title="Public transit apps don't account for real-time delays",
                description="My bus is always late but the app shows the scheduled time. Need actual real-time arrival predictions based on traffic and current location.",
                category="Transportation",
                subcategory="Public Transit",
                severity=3,
                validation_count=289,
                growth_rate=13.6,
                market_size="$50M-$100M",
                geographic_scope="local",
                country="United States",
                region="Massachusetts",
                city="Boston",
                author_id=users[0].id,
                completion_status="open",
                status="active"
            ),
            Opportunity(
                title="Coordinating carpools for kids' activities is a headache",
                description="Parents in our neighborhood want to carpool for sports and activities but coordinating schedules manually via text is chaotic.",
                category="Transportation",
                subcategory="Ridesharing",
                severity=2,
                validation_count=178,
                growth_rate=9.4,
                market_size="$10M-$50M",
                geographic_scope="local",
                country="United States",
                region="Texas",
                city="Austin",
                author_id=users[1].id,
                completion_status="open",
                status="active"
            ),

            # Shopping & Services
            Opportunity(
                title="International shipping costs are too high for small businesses",
                description="As a small e-commerce business, international shipping eats into our margins. Need affordable international shipping solutions.",
                category="Shopping & Services",
                subcategory="E-commerce",
                severity=4,
                validation_count=278,
                growth_rate=14.2,
                market_size="$500M+",
                geographic_scope="international",
                author_id=users[1].id,
                completion_status="open",
                status="active"
            ),
            Opportunity(
                title="Grocery delivery apps have inconsistent substitutions",
                description="When items are out of stock, shoppers make terrible substitutions. I need better control over what substitutions are acceptable.",
                category="Shopping & Services",
                subcategory="Groceries",
                severity=2,
                validation_count=198,
                growth_rate=7.3,
                market_size="$50M-$100M",
                geographic_scope="regional",
                country="United States",
                region="California",
                author_id=users[2].id,
                completion_status="open",
                status="active"
            ),
            Opportunity(
                title="Finding same-day dry cleaning pickup is impossible",
                description="I need dry cleaning picked up and returned quickly for work travel, but same-day service is hard to find and unreliable.",
                category="Shopping & Services",
                subcategory="Personal Services",
                severity=2,
                validation_count=134,
                growth_rate=5.8,
                market_size="$10M-$50M",
                geographic_scope="local",
                country="United States",
                region="Illinois",
                city="Chicago",
                author_id=users[0].id,
                completion_status="open",
                status="active"
            ),

            # Work & Productivity
            Opportunity(
                title="Video calls are exhausting and hard to focus on",
                description="Back-to-back video meetings leave me drained. I need better tools to stay engaged and manage meeting fatigue.",
                category="Work & Productivity",
                subcategory="Remote Work",
                severity=3,
                validation_count=412,
                growth_rate=17.2,
                market_size="$100M-$500M",
                geographic_scope="online",
                author_id=users[1].id,
                completion_status="open",
                status="active"
            ),
            Opportunity(
                title="Managing freelance contracts and agreements is confusing",
                description="I need legal contract templates and guidance for freelance work but can't afford a lawyer for every project.",
                category="Work & Productivity",
                subcategory="Legal",
                severity=4,
                validation_count=267,
                growth_rate=15.9,
                market_size="$50M-$100M",
                geographic_scope="online",
                author_id=users[2].id,
                completion_status="open",
                status="active"
            ),
            Opportunity(
                title="Coworking spaces don't have flexible hourly booking",
                description="I only need a desk for 2-3 hours occasionally, but coworking spaces only offer monthly memberships or expensive day passes.",
                category="Work & Productivity",
                subcategory="Workspace",
                severity=2,
                validation_count=156,
                growth_rate=8.1,
                market_size="$10M-$50M",
                geographic_scope="regional",
                country="United States",
                region="Washington",
                city="Seattle",
                author_id=users[0].id,
                completion_status="open",
                status="active"
            ),

            # Education & Learning
            Opportunity(
                title="Finding tutors for specialized subjects is difficult",
                description="My child needs help with advanced math but finding qualified tutors in our area who specialize in this is nearly impossible.",
                category="Education & Learning",
                subcategory="Tutoring",
                severity=4,
                validation_count=301,
                growth_rate=18.7,
                market_size="$100M-$500M",
                geographic_scope="regional",
                country="United States",
                region="New York",
                author_id=users[1].id,
                completion_status="open",
                status="active"
            ),
            Opportunity(
                title="Online course completion rates are terrible",
                description="I buy online courses but never finish them. Need better accountability and learning structure to actually complete what I start.",
                category="Education & Learning",
                subcategory="Online Learning",
                severity=3,
                validation_count=478,
                growth_rate=21.3,
                market_size="$100M-$500M",
                geographic_scope="online",
                author_id=users[2].id,
                completion_status="open",
                status="active"
            ),

            # Entertainment & Social
            Opportunity(
                title="Finding local events that match my interests is hit-or-miss",
                description="I miss out on concerts, meetups, and events because I don't know they're happening. Current event apps are too generic.",
                category="Entertainment & Social",
                subcategory="Events",
                severity=2,
                validation_count=223,
                growth_rate=11.8,
                market_size="$50M-$100M",
                geographic_scope="local",
                country="United States",
                region="Colorado",
                city="Denver",
                author_id=users[0].id,
                completion_status="open",
                status="active"
            ),
            Opportunity(
                title="Splitting restaurant bills with friends is awkward",
                description="Every time we go out with friends, splitting the bill fairly is complicated and someone always overpays or underpays.",
                category="Entertainment & Social",
                subcategory="Dining",
                severity=2,
                validation_count=389,
                growth_rate=14.5,
                market_size="$50M-$100M",
                geographic_scope="online",
                author_id=users[1].id,
                completion_status="solved",
                status="active"
            ),

            # Pet Care
            Opportunity(
                title="Finding last-minute pet sitters when traveling is stressful",
                description="When travel plans change suddenly, I can't find reliable pet sitters. Boarding facilities are expensive and my dog gets anxious there.",
                category="Pet Care",
                subcategory="Pet Sitting",
                severity=4,
                validation_count=267,
                growth_rate=16.2,
                market_size="$50M-$100M",
                geographic_scope="local",
                country="United States",
                region="Florida",
                city="Miami",
                author_id=users[2].id,
                completion_status="open",
                status="active"
            ),

            # Technology
            Opportunity(
                title="Managing passwords across all my devices is a security risk",
                description="I reuse passwords because remembering unique ones for 50+ accounts is impossible. I know it's risky but password managers seem complicated.",
                category="Technology",
                subcategory="Security",
                severity=5,
                validation_count=534,
                growth_rate=23.4,
                market_size="$500M+",
                geographic_scope="online",
                author_id=None,
                is_anonymous=True,
                completion_status="solved",
                status="active"
            ),
            Opportunity(
                title="Smart home devices don't work well together",
                description="I have devices from different brands and they don't integrate. Need a universal controller that actually works with everything.",
                category="Technology",
                subcategory="Smart Home",
                severity=3,
                validation_count=342,
                growth_rate=19.8,
                market_size="$100M-$500M",
                geographic_scope="online",
                author_id=users[0].id,
                completion_status="in_progress",
                status="active"
            ),

            # Family & Parenting
            Opportunity(
                title="Coordinating family schedules with multiple kids is chaos",
                description="Between school, sports, activities, and appointments for 3 kids, our family calendar is a mess. Need better family coordination tools.",
                category="Family & Parenting",
                subcategory="Organization",
                severity=4,
                validation_count=398,
                growth_rate=22.1,
                market_size="$50M-$100M",
                geographic_scope="online",
                author_id=users[1].id,
                completion_status="open",
                status="active"
            ),
            Opportunity(
                title="Finding reliable babysitters for date nights is difficult",
                description="We don't have family nearby and finding trustworthy babysitters who are available on weekends is nearly impossible.",
                category="Family & Parenting",
                subcategory="Childcare",
                severity=3,
                validation_count=287,
                growth_rate=13.2,
                market_size="$50M-$100M",
                geographic_scope="local",
                country="United States",
                region="Oregon",
                city="Portland",
                author_id=users[2].id,
                completion_status="open",
                status="active"
            )
        ]

        db.add_all(opportunities)
        db.commit()

        print("Database initialized successfully!")
        print(f"Created {len(users)} users")
        print(f"Created {len(opportunities)} opportunities")
        print("\nSample credentials:")
        print("Email: demo@example.com")
        print("Password: demo123")

    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("Initializing database...")
    init_db()
