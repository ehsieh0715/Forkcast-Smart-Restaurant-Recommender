import uuid
from datetime import datetime, timezone

import pytest
from app.models import ComparisonSession, Restaurant, User

from app import create_app, db


# ----------------------------------------------
# Fixtures
# ----------------------------------------------
@pytest.fixture
def app_instance():
    """Create a Flask application instance for testing."""
    app = create_app(testing=True)  # Enable testing mode
    with app.app_context():  # Create application context
        db.create_all()  # Create all tables
        yield app  # Yield the app instance for tests
        db.session.remove()  # Remove the session
        db.drop_all()  # Drop all tables after tests


@pytest.fixture
def client(app_instance):
    """Create a test client for the Flask application."""
    return app_instance.test_client()  # Create a test client for making requests


@pytest.fixture
def seed_user_and_restaurant(app_instance):
    """Seed a user and a restaurant for testing comparison functionality."""
    with app_instance.app_context():  # Create application context
        user = User(  # Create a test user
            name="Test User", username="test_user", email="test_user@example.com"
        )
        db.session.add(user)  # Add user to the session
        db.session.commit()  # Commit the session to save user
        user_id = str(user.user_id)  # Get the user ID as a string
        restaurant = Restaurant(  # Create a test restaurant
            full_name="Test Restaurant",
            place_id="place-123",
            lat=40.7128,
            lon=-74.0060,
            phone="555-555",
            rating=4.7,
            review_count=99,
            address="123 Main St",
            cuisine_type="Italian",
            cuisine_keyword="pizza",
            inspection_grade="A",
        )
        db.session.add(restaurant)  # Add restaurant to the session
        db.session.commit()  # Commit the session to save restaurant
        restaurant_id = str(
            restaurant.restaurant_id
        )  # Get the restaurant ID as a string
        return user_id, restaurant_id  # Return user and restaurant IDs for tests


# ----------------------------------------------
# Test: Add and View Restaurant in Comparison Session
# ----------------------------------------------
def test_create_comparison_session(client, seed_user_and_restaurant):
    """Test creating a new comparison session."""
    user_id, _ = seed_user_and_restaurant  # Get the seeded user ID for testing

    # Create a new comparison session
    res = client.post("api/comparison/session/create", json={"user_id": user_id})
    data = res.get_json()  # Get the JSON response data
    assert res.status_code == 201  # Ensure the response status is 201 Created
    assert data["status"] == "success"  # Ensure the status in response is success
    assert (
        data["created_by"] == user_id
    )  # Ensure the session was created by the correct user
    assert "session_id" in data  # Ensure session_id is present in the response
    assert (
        "expires_at" not in data
    )  # Ensure expires_at is not included for a new session

    # Create another session for the same user to ensure reuse
    res2 = client.post("api/comparison/session/create", json={"user_id": user_id})
    data2 = res2.get_json()  # Get the JSON response data
    assert res2.status_code == 200  # Ensure the response status is 200 OK
    assert data2["status"] == "success"  # Ensure the status in response is success
    assert (
        data2["session_id"] == data["session_id"]
    )  # Ensure the session ID matches the first session


# ----------------------------------------------
# Test: Add and View Restaurant in Comparison Session
# ----------------------------------------------
def test_add_and_view_restaurant_in_session(client, seed_user_and_restaurant):
    """Test adding a restaurant to a comparison session and retrieving it."""
    user_id, restaurant_id = (
        seed_user_and_restaurant  # Get seeded user and restaurant IDs
    )

    # Create a new comparison session for the user
    res = client.post("api/comparison/session/create", json={"user_id": user_id})
    session_id = res.get_json()["session_id"]  # Extract session ID from response

    # Add a restaurant to the created session
    add_res = client.post(
        f"api/comparison/session/{session_id}/add_restaurant",
        json={"user_id": user_id, "restaurant_id": restaurant_id},
    )
    assert add_res.status_code == 200  # Ensure adding restaurant was successful
    assert add_res.get_json()["status"] == "success"  # Verify status is success

    # View the session to confirm the restaurant is included
    view_res = client.post(
        f"api/comparison/session/{session_id}/view", json={"user_id": user_id}
    )
    data = view_res.get_json()  # Get JSON response data
    assert view_res.status_code == 200  # Ensure viewing session was successful
    assert data["status"] == "success"  # Verify status is success
    assert data["session_id"] == session_id  # Ensure session_id matches
    # Ensure the restaurant appears in the returned restaurant list
    assert any(r["restaurant_id"] == restaurant_id for r in data["restaurants"])


# ----------------------------------------------
# Test: Remove Restaurant from Comparison Session
# ----------------------------------------------
def test_remove_restaurant_from_session(client, seed_user_and_restaurant):
    """Test removing a previously added restaurant from a comparison session."""
    user_id, restaurant_id = (
        seed_user_and_restaurant  # Get seeded user and restaurant IDs
    )

    # Create a new comparison session for the user
    res = client.post("api/comparison/session/create", json={"user_id": user_id})
    session_id = res.get_json()["session_id"]  # Extract session ID from response

    # Add the restaurant to the session first
    client.post(
        f"api/comparison/session/{session_id}/add_restaurant",
        json={"user_id": user_id, "restaurant_id": restaurant_id},
    )

    # Remove the restaurant from the session
    rem_res = client.post(
        f"api/comparison/session/{session_id}/remove_restaurant",
        json={"user_id": user_id, "restaurant_id": restaurant_id},
    )
    assert rem_res.status_code == 200  # Ensure removal response is successful
    assert rem_res.get_json()["status"] == "success"  # Verify status is success

    # View the session to confirm restaurant has been removed
    view_res = client.post(
        f"api/comparison/session/{session_id}/view", json={"user_id": user_id}
    )
    restaurants = view_res.get_json()[
        "restaurants"
    ]  # Get list of restaurants in session
    # Ensure the removed restaurant is no longer present
    assert all(r["restaurant_id"] != restaurant_id for r in restaurants)


# ----------------------------------------------
# Test: Get All Comparison Sessions for a User
# ----------------------------------------------
def test_get_user_comparison_sessions(client, seed_user_and_restaurant):
    """Test retrieving all comparison sessions belonging to a specific user."""
    user_id, _ = (
        seed_user_and_restaurant  # Get seeded user ID (restaurant_id not needed)
    )

    # Create a comparison session for the user
    client.post("api/comparison/session/create", json={"user_id": user_id})
    # Attempt to create another session (should reuse existing session)
    client.post("api/comparison/session/create", json={"user_id": user_id})

    # Retrieve all comparison sessions for this user
    res = client.get(f"api/comparison/user/{user_id}/sessions")
    data = res.get_json()  # Parse JSON response

    assert res.status_code == 200  # Ensure response status is OK
    assert data["status"] == "success"  # Verify status is success
    assert isinstance(data["sessions"], list)  # Ensure sessions field is a list
    assert len(data["sessions"]) == 1  # Only one active session should exist

    # Validate session fields
    for s in data["sessions"]:
        assert "session_id" in s  # Session ID must be present
        assert "restaurant_count" in s  # Restaurant count must be present
