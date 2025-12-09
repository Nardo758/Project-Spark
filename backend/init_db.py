"""
Initialize the database with sample data
Run this script after starting the database to populate it with test data
"""

from app.db.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.opportunity import Opportunity
from app.core.security import get_password_hash

def init_db():
    """Initialize database with sample data"""

    # Create tables
    Base.metadata.create_all(bind=engine)

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
                completion_status="open",
                status="active"
            ),
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
                author_id=None,  # Anonymous
                is_anonymous=True,
                completion_status="open",
                status="active"
            ),
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
