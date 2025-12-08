"""
Initialize database with sample categories and data
"""
from app.core.database import SessionLocal, engine, Base
from app.models.category import Category
from app.models.user import User
from app.core.security import get_password_hash

# Create all tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Create sample categories
categories = [
    {
        "name": "SaaS & Business Tools",
        "slug": "saas-business",
        "description": "Software and tools for businesses",
        "icon": "💼",
        "color": "#4F46E5"
    },
    {
        "name": "Developer Tools",
        "slug": "dev-tools",
        "description": "Tools and platforms for developers",
        "icon": "👨‍💻",
        "color": "#10B981"
    },
    {
        "name": "E-commerce",
        "slug": "ecommerce",
        "description": "Online shopping and retail",
        "icon": "🛒",
        "color": "#F59E0B"
    },
    {
        "name": "Healthcare",
        "slug": "healthcare",
        "description": "Medical and health services",
        "icon": "🏥",
        "color": "#EF4444"
    },
    {
        "name": "Education",
        "slug": "education",
        "description": "Learning and educational platforms",
        "icon": "📚",
        "color": "#8B5CF6"
    },
    {
        "name": "Finance",
        "slug": "finance",
        "description": "Financial services and fintech",
        "icon": "💰",
        "color": "#06B6D4"
    },
    {
        "name": "Marketing",
        "slug": "marketing",
        "description": "Marketing tools and services",
        "icon": "📊",
        "color": "#EC4899"
    },
    {
        "name": "Productivity",
        "slug": "productivity",
        "description": "Productivity and collaboration tools",
        "icon": "⚡",
        "color": "#F97316"
    }
]

# Check if categories already exist
existing_categories = db.query(Category).count()
if existing_categories == 0:
    print("Creating sample categories...")
    for cat_data in categories:
        category = Category(**cat_data)
        db.add(category)
    db.commit()
    print(f"✓ Created {len(categories)} categories")
else:
    print(f"Categories already exist ({existing_categories} found)")

# Create a test user
existing_user = db.query(User).filter(User.email == "test@example.com").first()
if not existing_user:
    print("Creating test user...")
    test_user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password=get_password_hash("password123"),
        is_active=True,
        is_verified=True
    )
    db.add(test_user)
    db.commit()
    print("✓ Created test user (email: test@example.com, password: password123)")
else:
    print("Test user already exists")

db.close()
print("\n✓ Database initialization complete!")
