import uuid  # For generating UUIDs
from datetime import datetime, timezone  # For timestamps

import pytest  # Pytest framework for fixtures and test functions
from app.models import ComparisonSession  # Import relevant models
from app.models import Restaurant, User

from app import create_app, db  # Import app factory and database

# -----------------------------
# FIXTURES
# -----------------------------


@pytest.fixture
def app_instance():
    """Create a fresh Flask app with in-memory DB and clean up after each test."""
    app = create_app(testing=True)  # Create the app in testing mode
    with app.app_context():  # Push an application context
        db.create_all()  # Create all database tables
        yield app  # Yield app instance for tests
        db.session.remove()  # Remove session after tests
        db.drop_all()  # Drop all tables after tests


@pytest.fixture
def client(app_instance):
    """Provide a test client bound to the app instance."""
    return app_instance.test_client()  # Return the test client


@pytest.fixture
def test_user(app_instance):
    """Insert a test user and return its UUID as a string."""
    with app_instance.app_context():  # Push app context
        user_id = uuid.uuid4()  # Generate unique user ID
        user = User(  # Create a user object
            user_id=user_id,
            name="Tester",
            username="tester",
            email="tester@example.com",
            password_hash=None,
        )
        db.session.add(user)  # Add to session
        db.session.commit()  # Commit to DB
        return str(user_id)  # Return the user_id as string


@pytest.fixture
def active_session(app_instance, test_user):
    """Create a comparison session (no expiration) and return its ID."""
    with app_instance.app_context():  # Push app context
        session_id = uuid.uuid4()  # Generate unique session ID
        now = datetime.now(timezone.utc)  # Current UTC time
        session = ComparisonSession(  # Create session object
            session_id=session_id,
            created_by=uuid.UUID(test_user),
            created_at=now,
            restaurants_json=[],
        )
        db.session.add(session)  # Add to session
        db.session.commit()  # Commit to DB
        return str(session_id)  # Return session_id as string


@pytest.fixture
def test_restaurant(app_instance):
    """Insert a dummy restaurant into the database and return its ID."""
    with app_instance.app_context():  # Push app context
        r_id = uuid.uuid4()  # Generate restaurant ID
        restaurant = Restaurant(  # Create restaurant object
            restaurant_id=r_id,
            place_id="place-123",
            full_name="Test Resto",
            address="123 Main St",
            rating=4.0,
            review_count=50,
            cuisine_type="Italian",
            cuisine_keyword="pizza",
            inspection_grade="A",
            lat=40.0,
            lon=-74.0,
            phone="555-1234",
            image_url="http://example.com/img.jpg",
            google_name="Test Google Resto",
            grid_id=None,
        )
        db.session.add(restaurant)  # Add to session
        db.session.commit()  # Commit to DB
        return str(r_id)  # Return restaurant ID as string


# -----------------------------
# TESTS
# -----------------------------


def test_create_comparison_session(client, test_user):
    """POST api/comparison/session/create should create a session."""
    res = client.post(
        "api/comparison/session/create", json={"user_id": test_user}
    )  # Call API
    data = res.get_json()  # Parse response
    assert res.status_code == 201  # Should create successfully
    assert data["status"] == "success"  # Status should be success
    assert data["created_by"] == test_user  # Created_by should match
    assert "session_id" in data  # Session ID should be in response
    assert "expires_at" not in data  # Expires_at should not be included


def test_add_restaurant_to_comparison(
    client, active_session, test_user, test_restaurant
):
    """POST api/comparison/session/<id>/add_restaurant should add restaurant."""
    res = client.post(  # Add restaurant to session
        f"api/comparison/session/{active_session}/add_restaurant",
        json={"user_id": test_user, "restaurant_id": test_restaurant},
    )
    data = res.get_json()  # Parse response
    assert res.status_code == 200  # Should succeed
    assert data["status"] == "success"  # Status should be success


def test_add_restaurant_to_comparison_unauthorized(
    client, active_session, test_restaurant
):
    """Should reject adding if user is not owner."""
    other_user = str(uuid.uuid4())  # Generate unrelated user ID
    res = client.post(  # Try to add restaurant as non-owner
        f"api/comparison/session/{active_session}/add_restaurant",
        json={"user_id": other_user, "restaurant_id": test_restaurant},
    )
    data = res.get_json()  # Parse response
    assert res.status_code == 403  # Should be forbidden
    assert data["status"] == "error"  # Status should be error


def test_remove_restaurant_from_comparison(
    client, active_session, test_user, test_restaurant
):
    """POST api/remove_restaurant should remove restaurant."""
    client.post(  # Add restaurant first
        f"api/comparison/session/{active_session}/add_restaurant",
        json={"user_id": test_user, "restaurant_id": test_restaurant},
    )
    res = client.post(  # Remove restaurant
        f"api/comparison/session/{active_session}/remove_restaurant",
        json={"user_id": test_user, "restaurant_id": test_restaurant},
    )
    data = res.get_json()  # Parse response
    assert res.status_code == 200  # Should succeed
    assert data["status"] == "success"  # Status should be success


def test_view_comparison_session(client, active_session, test_user, test_restaurant):
    """POST api/comparison/session/<id>/view should show details."""
    client.post(  # Add restaurant before viewing
        f"api/comparison/session/{active_session}/add_restaurant",
        json={"user_id": test_user, "restaurant_id": test_restaurant},
    )
    res = client.post(  # View session
        f"api/comparison/session/{active_session}/view", json={"user_id": test_user}
    )
    data = res.get_json()  # Parse response
    assert res.status_code == 200  # Should succeed
    assert data["status"] == "success"  # Status should be success
    assert data["session_id"] == active_session  # Session ID should match
    assert isinstance(data["restaurants"], list)  # Restaurants field should be list
    assert (
        data["restaurants"][0]["restaurant_id"] == test_restaurant
    )  # Restaurant ID should match


def test_get_user_comparison_sessions(client, active_session, test_user):
    """GET api/comparison/user/<id>/sessions should list sessions."""
    res = client.get(f"api/comparison/user/{test_user}/sessions")  # GET sessions
    data = res.get_json()  # Parse response
    assert res.status_code == 200  # Should succeed
    assert data["status"] == "success"  # Status should be success
    assert isinstance(data["sessions"], list)  # Sessions should be a list
    assert (
        data["sessions"][0]["session_id"] == active_session
    )  # Session ID should match
