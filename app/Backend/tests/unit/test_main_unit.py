import uuid  # For generating UUIDs in tests
from datetime import datetime  # For timestamps in dummy predictions
from unittest.mock import patch  # Patch for mocking database interactions

import pytest  # Pytest for fixtures and assertions
from flask import Flask  # Flask for creating a minimal app instance


# --------------------------------------------------------
# Dummy classes that simulate SQLAlchemy model instances
# --------------------------------------------------------
class DummyRestaurant:
    """A dummy restaurant object simulating a row from the Restaurant model."""

    def __init__(self):
        self.restaurant_id = uuid.uuid4()  # Unique restaurant ID
        self.place_id = "rest1"  # Sample place_id
        self.full_name = "Test Resto"  # Full name
        self.rating = 4.7  # Average rating
        self.review_count = 120  # Number of reviews
        self.cuisine_keyword = "Mexican"  # Cuisine keyword
        self.grid_id = "grid1"  # Grid reference
        self.address = "123 Test St"  # Address
        self.inspection_grade = "A"  # Inspection grade
        self.cuisine_type = "Mexican"  # Cuisine type
        self.lat = 40.7  # Latitude
        self.lon = -74.0  # Longitude
        self.phone = "1234567890"  # Contact number
        self.image_url = "img.jpg"  # Image URL
        self.google_name = "Google Resto"  # Google name
        self.inspection_id = None
        self.inspection_date = None
        self.restaurant_counts = 45
        self.geometry = None
        self.price_level = 2
        self.has_opening_hour_data = True
        self.has_popular_hour_data = True
        self.lat_rounded = 40.7
        self.lon_rounded = -74.0
        self.wheelchair_friendly = True
        self.opening_hours = {"Monday": ["09:00–17:00"]}
        self.amenities = ["WiFi", "Outdoor seating"]


class DummyPrediction:
    """A dummy prediction object simulating a row from the BusynessPrediction model."""

    def __init__(self, predicted_level, timestamp=None):
        self.predicted_level = predicted_level  # Predicted busyness level
        self.timestamp = timestamp or datetime(
            2025, 1, 1, 12, 0
        )  # Prediction timestamp
        self.grid_id = "grid1"  # Grid reference


# --------------------------------------------------------
# Flask test client fixture with `main` blueprint loaded
# --------------------------------------------------------
@pytest.fixture
def client():
    """Fixture that creates a Flask app and registers the main blueprint."""
    from app.routes.main_routes import main  # Import main blueprint

    app = Flask(__name__)  # Create minimal Flask app
    app.register_blueprint(main, url_prefix="/api")  # Register blueprint
    app.config["TESTING"] = True  # Enable testing mode
    return app.test_client()  # Return test client


# --------------------------------------------------------
# Root and Healthcheck routes
# --------------------------------------------------------
def test_home(client):
    """Test that the root route returns the expected message."""
    response = client.get("api/")  # GET /
    assert response.status_code == 200  # Should return OK
    assert (
        response.get_json()["message"]
        == "Restaurant Busyness Predictor backend is running."
    )


def test_healthcheck(client):
    """Test that the healthcheck route returns status ok."""
    response = client.get("api/healthcheck")  # GET /healthcheck
    assert response.status_code == 200  # Should return OK
    assert response.get_json()["status"] == "ok"  # Status should be ok


# --------------------------------------------------------
# /restaurants (list all)
# --------------------------------------------------------
@patch("app.routes.main_routes.db")
def test_list_all_restaurants(mock_db, client):
    """Test that listing all restaurants returns expected fields."""
    dummy_restaurant = DummyRestaurant()  # Create dummy restaurant
    dummy_prediction = DummyPrediction(predicted_level=4.0)  # Create dummy prediction

    # Mock database calls
    mock_db.session.query.return_value.all.return_value = [
        dummy_restaurant
    ]  # Mock restaurant query
    mock_db.session.execute.return_value.fetchone.return_value = (
        dummy_prediction  # Mock prediction fetch
    )

    response = client.get("api/restaurants")  # GET /restaurants
    data = response.get_json()
    assert response.status_code == 200  # Should return OK
    assert data["status"] == "success"  # Status should be success
    assert data["restaurants"][0]["restaurant_id"] == str(
        dummy_restaurant.restaurant_id
    )  # ID matches


# --------------------------------------------------------
# /restaurants/<restaurant_id> (details)
# --------------------------------------------------------
@patch("app.routes.main_routes.db")
def test_get_restaurant_details_success(mock_db, client):
    """Test retrieving detailed info for a valid restaurant."""
    dummy_restaurant = DummyRestaurant()  # Dummy restaurant
    dummy_prediction = DummyPrediction(predicted_level=2.7)  # Dummy prediction

    # Mock restaurant retrieval
    mock_db.session.query.return_value.filter_by.return_value.first.return_value = (
        dummy_restaurant
    )
    # Mock prediction retrieval
    mock_db.session.execute.return_value.fetchone.return_value = dummy_prediction

    response = client.get(
        f"api/restaurants/{dummy_restaurant.restaurant_id}"
    )  # GET restaurant details
    data = response.get_json()
    assert response.status_code == 200  # Should return OK
    assert data["restaurant_id"] == str(dummy_restaurant.restaurant_id)  # ID matches
    assert data["full_name"] == dummy_restaurant.full_name  # Name matches
    assert data["predicted_level"] == dummy_prediction.predicted_level  # Level matches


@patch("app.routes.main_routes.db")
def test_get_restaurant_details_not_found(mock_db, client):
    """Test retrieving details for a non-existent restaurant."""
    mock_db.session.query.return_value.filter_by.return_value.first.return_value = (
        None  # Mock not found
    )
    response = client.get(f"api/restaurants/{uuid.uuid4()}")  # GET with random ID
    assert response.status_code == 404  # Should return not found
    assert "error" in response.get_json()  # Error key present


# --------------------------------------------------------
# /restaurants/<id>/busyness
# --------------------------------------------------------
@patch("app.routes.main_routes.db")
def test_get_restaurant_busyness_success(mock_db, client):
    """Test retrieving busyness data for a valid restaurant."""
    dummy_restaurant = DummyRestaurant()  # Dummy restaurant
    dummy_prediction = DummyPrediction(predicted_level=3.4)  # Dummy prediction

    # Mock restaurant and prediction retrieval
    mock_db.session.query.return_value.filter_by.return_value.first.return_value = (
        dummy_restaurant
    )
    mock_db.session.execute.return_value.fetchone.return_value = dummy_prediction

    response = client.get(
        f"api/restaurants/{dummy_restaurant.restaurant_id}/busyness"
    )  # GET busyness
    data = response.get_json()
    assert response.status_code == 200  # Should return OK
    assert data["full_name"] == dummy_restaurant.full_name  # Name matches
    assert data["predicted_level"] == dummy_prediction.predicted_level  # Level matches


# --------------------------------------------------------
# /restaurants/predictions
# --------------------------------------------------------
@patch("app.routes.main_routes.db")
def test_get_all_restaurant_predictions(mock_db, client):
    """Test retrieving predictions for all restaurants."""
    dummy_restaurant = DummyRestaurant()  # Dummy restaurant
    dummy_prediction = DummyPrediction(predicted_level=4.2)  # Dummy prediction

    # Mock DB responses
    mock_db.session.query.return_value.all.return_value = [dummy_restaurant]
    mock_db.session.execute.return_value.fetchone.return_value = dummy_prediction

    response = client.get("api/restaurants/predictions")  # GET predictions
    data = response.get_json()
    assert response.status_code == 200  # Should return OK
    assert data["status"] == "success"  # Status should be success
    assert data["predictions"][0]["restaurant_id"] == str(
        dummy_restaurant.restaurant_id
    )  # ID matches
    assert (
        data["predictions"][0]["restaurant_full_name"] == dummy_restaurant.full_name
    )  # Name matches
    assert (
        data["predictions"][0]["predicted_busyness"] == dummy_prediction.predicted_level
    )  # Level matches


# --------------------------------------------------------
# /filters/options
# --------------------------------------------------------
@patch("app.routes.main_routes.db")
def test_get_filter_options(mock_db, client):
    """Test retrieving filter options includes seeded cuisines."""
    # Mock cuisines query returning tuples
    mock_db.session.query.return_value.all.return_value = [
        ("Mexican, Chinese",),
        ("Italian",),
        ("chinese",),
    ]

    response = client.get("api/filters/options")  # GET filters
    data = response.get_json()
    assert response.status_code == 200  # Should return OK
    assert data["status"] == "success"  # Status should be success
    expected_cuisines = {"Mexican", "Chinese", "Italian", "chinese"}  # Expected set
    actual = set(data["filters"]["cuisine_types"])  # Extract cuisines from response
    assert expected_cuisines.issubset(actual)  # All expected cuisines present
