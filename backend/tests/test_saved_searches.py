"""
Tests for Saved Searches API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from app.main import app
from app.db.database import Base, get_db
from app.models.user import User
from app.models.saved_search import SavedSearch
from app.models.opportunity import Opportunity
from app.models.subscription import UserSubscription, SubscriptionTier
from app.core.security import create_access_token

# Test database setup
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_saved_searches.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create test database"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Create test client"""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db):
    """Create a test user"""
    user = User(
        email="test@example.com",
        name="Test User",
        hashed_password="hashed_password_here",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def pro_user(db):
    """Create a pro-tier test user"""
    user = User(
        email="pro@example.com",
        name="Pro User",
        hashed_password="hashed_password_here",
        is_active=True
    )
    db.add(user)
    db.commit()
    
    # Add pro subscription
    subscription = UserSubscription(
        user_id=user.id,
        tier=SubscriptionTier.PRO,
        is_active=True,
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=365)
    )
    db.add(subscription)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    """Generate auth headers"""
    token = create_access_token(data={"sub": test_user.email})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def pro_auth_headers(pro_user):
    """Generate auth headers for pro user"""
    token = create_access_token(data={"sub": pro_user.email})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_opportunities(db):
    """Create sample opportunities for testing"""
    opportunities = [
        Opportunity(
            title="E-commerce shipping inefficiency",
            description="Small e-commerce sellers struggle with shipping costs",
            category="Work & Productivity",
            feasibility_score=85,
            validation_count=120,
            status="active",
            moderation_status="approved",
            geographic_scope="international"
        ),
        Opportunity(
            title="Freelance invoicing headaches",
            description="Freelancers waste time on invoicing and payment tracking",
            category="Work & Productivity",
            feasibility_score=78,
            validation_count=95,
            status="active",
            moderation_status="approved",
            geographic_scope="online"
        ),
        Opportunity(
            title="Local fitness class discovery",
            description="Hard to find local fitness classes that match schedule",
            category="Health & Wellness",
            feasibility_score=62,
            validation_count=45,
            status="active",
            moderation_status="approved",
            geographic_scope="local",
            country="USA"
        )
    ]
    
    for opp in opportunities:
        db.add(opp)
    
    db.commit()
    return opportunities


# ========== Saved Search CRUD Tests ==========

def test_create_saved_search(client, auth_headers, db):
    """Test creating a saved search"""
    
    payload = {
        "name": "High Feasibility Tech Opportunities",
        "filters": {
            "category": "Work & Productivity",
            "min_feasibility": 75,
            "sort_by": "feasibility"
        },
        "notification_prefs": {
            "email": True,
            "push": False,
            "slack": False,
            "frequency": "daily"
        }
    }
    
    response = client.post("/api/v1/saved-searches/", json=payload, headers=auth_headers)
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["filters"] == payload["filters"]
    assert data["is_active"] is True


def test_create_saved_search_free_tier_limit(client, auth_headers, db, test_user):
    """Test free tier can only create 1 saved search"""
    
    # Create first saved search (should succeed)
    payload = {
        "name": "Search 1",
        "filters": {"category": "Tech"},
        "notification_prefs": {"email": True, "frequency": "daily"}
    }
    
    response = client.post("/api/v1/saved-searches/", json=payload, headers=auth_headers)
    assert response.status_code == 201
    
    # Try to create second saved search (should fail)
    payload2 = {
        "name": "Search 2",
        "filters": {"category": "Finance"},
        "notification_prefs": {"email": True, "frequency": "daily"}
    }
    
    response = client.post("/api/v1/saved-searches/", json=payload2, headers=auth_headers)
    assert response.status_code == 403
    assert "Free tier limited" in response.json()["detail"]


def test_create_saved_search_pro_tier(client, pro_auth_headers, db):
    """Test pro tier can create up to 10 saved searches"""
    
    # Create 10 saved searches (should all succeed)
    for i in range(10):
        payload = {
            "name": f"Search {i+1}",
            "filters": {"category": "Tech"},
            "notification_prefs": {"email": True, "frequency": "daily"}
        }
        
        response = client.post("/api/v1/saved-searches/", json=payload, headers=pro_auth_headers)
        assert response.status_code == 201
    
    # Try to create 11th (should fail)
    payload = {
        "name": "Search 11",
        "filters": {"category": "Tech"},
        "notification_prefs": {"email": True, "frequency": "daily"}
    }
    
    response = client.post("/api/v1/saved-searches/", json=payload, headers=pro_auth_headers)
    assert response.status_code == 403


def test_get_saved_searches(client, auth_headers, db, test_user):
    """Test retrieving saved searches"""
    
    # Create a saved search directly in DB
    search = SavedSearch(
        user_id=test_user.id,
        name="Test Search",
        filters={"category": "Tech"},
        notification_prefs={"email": True, "frequency": "daily"},
        is_active=True
    )
    db.add(search)
    db.commit()
    
    response = client.get("/api/v1/saved-searches/", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["saved_searches"]) == 1
    assert data["saved_searches"][0]["name"] == "Test Search"


def test_get_saved_search_by_id(client, auth_headers, db, test_user):
    """Test retrieving a specific saved search"""
    
    search = SavedSearch(
        user_id=test_user.id,
        name="Test Search",
        filters={"category": "Tech"},
        notification_prefs={"email": True, "frequency": "daily"},
        is_active=True
    )
    db.add(search)
    db.commit()
    db.refresh(search)
    
    response = client.get(f"/api/v1/saved-searches/{search.id}", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == search.id
    assert data["name"] == "Test Search"


def test_update_saved_search(client, auth_headers, db, test_user):
    """Test updating a saved search"""
    
    search = SavedSearch(
        user_id=test_user.id,
        name="Original Name",
        filters={"category": "Tech"},
        notification_prefs={"email": True, "frequency": "daily"},
        is_active=True
    )
    db.add(search)
    db.commit()
    db.refresh(search)
    
    update_payload = {
        "name": "Updated Name",
        "notification_prefs": {"email": False, "push": True, "frequency": "instant"}
    }
    
    response = client.patch(
        f"/api/v1/saved-searches/{search.id}", 
        json=update_payload, 
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["notification_prefs"]["push"] is True


def test_delete_saved_search_soft(client, auth_headers, db, test_user):
    """Test soft-deleting a saved search"""
    
    search = SavedSearch(
        user_id=test_user.id,
        name="Test Search",
        filters={"category": "Tech"},
        notification_prefs={"email": True, "frequency": "daily"},
        is_active=True
    )
    db.add(search)
    db.commit()
    db.refresh(search)
    
    response = client.delete(f"/api/v1/saved-searches/{search.id}", headers=auth_headers)
    
    assert response.status_code == 204
    
    # Verify it's soft-deleted
    db.refresh(search)
    assert search.is_active is False


def test_delete_saved_search_hard(client, auth_headers, db, test_user):
    """Test hard-deleting a saved search"""
    
    search = SavedSearch(
        user_id=test_user.id,
        name="Test Search",
        filters={"category": "Tech"},
        notification_prefs={"email": True, "frequency": "daily"},
        is_active=True
    )
    db.add(search)
    db.commit()
    search_id = search.id
    
    response = client.delete(
        f"/api/v1/saved-searches/{search_id}?hard_delete=true", 
        headers=auth_headers
    )
    
    assert response.status_code == 204
    
    # Verify it's permanently deleted
    deleted = db.query(SavedSearch).filter(SavedSearch.id == search_id).first()
    assert deleted is None


def test_test_saved_search(client, auth_headers, db, test_user, sample_opportunities):
    """Test the test endpoint that shows current matches"""
    
    search = SavedSearch(
        user_id=test_user.id,
        name="Work Productivity",
        filters={"category": "Work & Productivity", "min_feasibility": 70},
        notification_prefs={"email": True, "frequency": "daily"},
        is_active=True
    )
    db.add(search)
    db.commit()
    db.refresh(search)
    
    response = client.post(f"/api/v1/saved-searches/{search.id}/test", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "current_matches" in data
    assert data["current_matches"] == 2  # Two Work & Productivity opps with feasibility >= 70
    assert len(data["opportunities"]) == 2


# ========== Recommended Opportunities Tests ==========

def test_get_recommended_opportunities(client, auth_headers, db, test_user, sample_opportunities):
    """Test getting personalized recommendations"""
    
    # Create some validation history for the user (simulating interest in Work & Productivity)
    from app.models.validation import Validation
    
    validation = Validation(
        user_id=test_user.id,
        opportunity_id=sample_opportunities[0].id
    )
    db.add(validation)
    db.commit()
    
    response = client.get("/api/v1/opportunities/recommended?limit=5", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "opportunities" in data
    assert "user_interests" in data
    assert "Work & Productivity" in data["user_interests"]
    
    # Should prioritize Work & Productivity opportunities
    if data["opportunities"]:
        assert data["opportunities"][0]["match_score"] is not None


def test_recommended_excludes_validated(client, auth_headers, db, test_user, sample_opportunities):
    """Test that recommended endpoint excludes already-validated opportunities"""
    
    from app.models.validation import Validation
    
    # User validates all opportunities
    for opp in sample_opportunities:
        validation = Validation(
            user_id=test_user.id,
            opportunity_id=opp.id
        )
        db.add(validation)
    db.commit()
    
    response = client.get("/api/v1/opportunities/recommended?limit=10", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    
    # Should return no opportunities (all validated)
    assert len(data["opportunities"]) == 0


# ========== Background Job Tests ==========

def test_find_matching_opportunities(db, test_user, sample_opportunities):
    """Test finding opportunities that match search filters"""
    
    from app.services.saved_search_alerts import find_matching_opportunities
    
    search = SavedSearch(
        user_id=test_user.id,
        name="Test Search",
        filters={
            "category": "Work & Productivity",
            "min_feasibility": 70
        },
        notification_prefs={"email": True, "frequency": "daily"},
        is_active=True
    )
    db.add(search)
    db.commit()
    
    matches = find_matching_opportunities(search, db, test_mode=True)
    
    # Should match 2 Work & Productivity opportunities with feasibility >= 70
    assert len(matches) == 2
    assert all(opp.category == "Work & Productivity" for opp in matches)
    assert all(opp.feasibility_score >= 70 for opp in matches)


def test_should_send_alert_frequency(db, test_user):
    """Test alert frequency logic"""
    
    from app.services.saved_search_alerts import should_send_alert
    
    # Never notified - should send
    search = SavedSearch(
        user_id=test_user.id,
        name="Test",
        filters={},
        notification_prefs={"email": True, "frequency": "daily"},
        is_active=True,
        last_notified_at=None
    )
    
    assert should_send_alert(search) is True
    
    # Notified 1 hour ago, daily frequency - should not send
    search.last_notified_at = datetime.utcnow() - timedelta(hours=1)
    assert should_send_alert(search) is False
    
    # Notified 25 hours ago, daily frequency - should send
    search.last_notified_at = datetime.utcnow() - timedelta(hours=25)
    assert should_send_alert(search) is True
    
    # Instant frequency, notified 5 minutes ago - should not send (rate limited)
    search.notification_prefs = {"email": True, "frequency": "instant"}
    search.last_notified_at = datetime.utcnow() - timedelta(minutes=5)
    assert should_send_alert(search) is False
    
    # Instant frequency, notified 15 minutes ago - should send
    search.last_notified_at = datetime.utcnow() - timedelta(minutes=15)
    assert should_send_alert(search) is True


def test_no_notifications_when_disabled(db, test_user):
    """Test that alerts aren't sent when all notification methods disabled"""
    
    from app.services.saved_search_alerts import should_send_alert
    
    search = SavedSearch(
        user_id=test_user.id,
        name="Test",
        filters={},
        notification_prefs={"email": False, "push": False, "slack": False, "frequency": "daily"},
        is_active=True
    )
    
    assert should_send_alert(search) is False


# ========== Match Score Tests ==========

def test_calculate_match_score(db, test_user, sample_opportunities):
    """Test match score calculation"""
    
    from app.routers.opportunities import calculate_match_score
    
    user_interests = ["Work & Productivity"]
    opp = sample_opportunities[0]  # High feasibility Work & Productivity
    
    score = calculate_match_score(opp, test_user, user_interests, db)
    
    # Should get high score:
    # Base 50 + Category match 20 + High feasibility 15 = 85
    assert score >= 85
    
    # Test with non-matching category
    opp2 = sample_opportunities[2]  # Health & Wellness
    score2 = calculate_match_score(opp2, test_user, user_interests, db)
    
    # Should get lower score (no category match)
    assert score2 < score


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
