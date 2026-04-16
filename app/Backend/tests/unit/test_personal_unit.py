import uuid  # Import uuid to generate UUIDs
from datetime import datetime  # Import datetime for timestamps
from unittest.mock import MagicMock, patch  # Import mock utilities

import pytest  # Import pytest for testing framework
from app.routes.personal_routes import \
    personal  # Import the personal blueprint
from flask import Flask  # Import Flask to create a test app


# -----------------------------
# FIXTURE: Create test client
# -----------------------------
@pytest.fixture
def client():  # Define a pytest fixture named client
    from app.routes.personal_routes import personal  # Import blueprint locally

    app = Flask(__name__)  # Create a Flask application
    app.register_blueprint(
        personal, url_prefix="/api"
    )  # Register the personal blueprint with prefix /api
    app.config["TESTING"] = True  # Enable testing mode for the app
    return app.test_client()  # Return the test client for requests


# -----------------------------
# TESTS: /personal/restaurant/<restaurant_id>/prediction
# -----------------------------
@patch("app.routes.personal_routes.func")  # Patch SQLAlchemy func to mock extract/abs
@patch(
    "app.routes.personal_routes.db"
)  # Patch the database session used in personal_routes
@patch(
    "app.routes.personal_routes.uuid.UUID",
    return_value=uuid.UUID("11111111-1111-1111-1111-111111111111"),
)  # Patch UUID parsing
def test_restaurant_prediction_success(
    mock_uuid, mock_db, mock_func, client
):  # Test function
    restaurant_uuid = uuid.UUID(
        "11111111-1111-1111-1111-111111111111"
    )  # Define fixed restaurant UUID
    mock_expr = MagicMock()  # Create a MagicMock for SQL expression
    mock_func.extract.return_value = mock_expr  # Mock extract to return mock expression
    mock_func.abs.return_value = mock_expr  # Mock abs to return mock expression
    mock_restaurant = MagicMock(
        grid_id="G1", restaurant_id=restaurant_uuid
    )  # Create mock restaurant object
    mock_prediction = MagicMock(
        timestamp=datetime(2025, 1, 1, 12, 0), predicted_level=3.5, grid_id="G1"
    )  # Create mock prediction
    restaurant_query = MagicMock()  # Create mock restaurant query
    restaurant_query.filter_by.return_value.first.return_value = (
        mock_restaurant  # Chain filter_by().first() to return mock restaurant
    )
    prediction_query = MagicMock()  # Create mock prediction query
    prediction_query.filter.return_value.order_by.return_value.first.return_value = (
        mock_prediction  # Chain to return mock prediction
    )
    mock_db.session.query.side_effect = [
        restaurant_query,
        prediction_query,
    ]  # Side effect to return both mocks
    res = client.get(
        f"api/personal/restaurant/{restaurant_uuid}/prediction?datetime=2025-01-01T12:00:00"
    )  # Call endpoint
    data = res.get_json()  # Get JSON response
    assert res.status_code == 200  # Assert response is OK
    assert data["restaurant_id"] == str(restaurant_uuid)  # Assert restaurant_id matches
    assert data["grid_id"] == "G1"  # Assert grid_id matches
    assert data["predicted_level"] == 3.5  # Assert predicted_level matches


@patch("app.routes.personal_routes.db")  # Patch database
@patch(
    "app.routes.personal_routes.uuid.UUID",
    return_value=uuid.UUID("11111111-1111-1111-1111-111111111111"),
)  # Patch UUID
def test_restaurant_prediction_no_prediction_found(
    mock_uuid, mock_db, client
):  # Test function
    mock_restaurant = MagicMock(
        grid_id="G1", restaurant_id=uuid.UUID("11111111-1111-1111-1111-111111111111")
    )  # Create mock restaurant
    restaurant_query = MagicMock()  # Mock restaurant query
    restaurant_query.filter_by.return_value.first.return_value = (
        mock_restaurant  # Return mock restaurant
    )
    prediction_query = MagicMock()  # Mock prediction query
    prediction_query.filter.return_value.order_by.return_value.first.return_value = (
        None  # Return no prediction
    )
    mock_db.session.query.side_effect = [
        restaurant_query,
        prediction_query,
    ]  # Side effect for queries
    res = client.get(
        "api/personal/restaurant/11111111-1111-1111-1111-111111111111/prediction?datetime=2025-01-01T12:00:00"
    )  # Call endpoint
    data = res.get_json()  # Parse response
    assert res.status_code == 404  # Assert 404 not found
    assert "No prediction data found" in data["message"]  # Assert error message


@patch("app.routes.personal_routes.db")  # Patch database
@patch(
    "app.routes.personal_routes.uuid.UUID",
    return_value=uuid.UUID("11111111-1111-1111-1111-111111111111"),
)  # Patch UUID
def test_restaurant_prediction_too_far_from_datetime(
    mock_uuid, mock_db, client
):  # Test function
    mock_restaurant = MagicMock(
        grid_id="G1", restaurant_id=uuid.UUID("11111111-1111-1111-1111-111111111111")
    )  # Mock restaurant
    mock_prediction = MagicMock(
        timestamp=datetime(2020, 1, 1, 12, 0), predicted_level=2.0, grid_id="G1"
    )  # Mock prediction far in time
    restaurant_query = MagicMock()  # Mock restaurant query
    restaurant_query.filter_by.return_value.first.return_value = (
        mock_restaurant  # Return mock restaurant
    )
    prediction_query = MagicMock()  # Mock prediction query
    prediction_query.filter.return_value.order_by.return_value.first.return_value = (
        mock_prediction  # Return mock prediction
    )
    mock_db.session.query.side_effect = [
        restaurant_query,
        prediction_query,
    ]  # Side effect
    res = client.get(
        "api/personal/restaurant/11111111-1111-1111-1111-111111111111/prediction?datetime=2025-01-01T12:00:00"
    )  # Call endpoint
    data = res.get_json()  # Parse response
    assert res.status_code == 404  # Assert 404 not found
    assert (
        "No prediction data close to requested datetime" in data["message"]
    )  # Assert error message


# -----------------------------
# TESTS: /personal/recommendation
# -----------------------------
from datetime import datetime


@patch("app.routes.personal_routes.db")
@patch("app.routes.personal_routes.calculate_personal_fit_score")
@patch("app.routes.personal_routes.get_filtered_candidates")
def test_personal_recommendation_success(mock_filter, mock_score, mock_db, client):
    mock_rest = MagicMock()
    mock_rest.restaurant_id = "mock-id"
    mock_rest.grid_id = "G1"
    mock_rest.full_name = "Mock Restaurant"
    mock_rest.google_name = "Mock G"
    mock_rest.cuisine_type = "Thai"
    mock_rest.rating = 4.3
    mock_rest.review_count = 88
    mock_rest.price_level = 2
    mock_rest.image_url = "http://example.com/mock.jpg"
    mock_filter.return_value = [mock_rest]

    # Build mock prediction with real timestamp
    mock_prediction = MagicMock()
    mock_prediction.predicted_level = 2.7
    mock_prediction.timestamp = datetime(2025, 1, 1, 18, 0, 0)  # real datetime object

    # Patch the filter().order_by().first() chain
    mock_db.session.query.return_value.filter.return_value.order_by.return_value.first.return_value = (
        mock_prediction
    )

    # Mock fit score calculation
    mock_score.return_value = (0.9, 750)

    payload = {
        "location": {"latitude": 40.7128, "longitude": -74.0060},
        "cuisine_preferences": ["Thai"],
        "price_level": "Medium",
        "desired_datetime": "2025-01-01T18:00:00",
    }

    res = client.post("api/personal/recommendation", json=payload)
    data = res.get_json()

    assert res.status_code == 200
    assert "recommendations" in data
    rec = data["recommendations"][0]
    assert rec["predicted_busyness"] == round(2.7, 2)
    assert rec["price_level"] == 2


def test_personal_recommendation_invalid_price_level(client):  # Test function
    payload = {  # Payload with invalid price_level
        "location": {"latitude": 40.7128, "longitude": -74.0060},
        "cuisine_preferences": ["Mexican"],
        "price_level": "Luxury",
        "desired_datetime": "2025-01-01T18:00:00",
    }
    res = client.post("api/personal/recommendation", json=payload)  # Call endpoint
    data = res.get_json()  # Parse response
    assert res.status_code == 400  # Assert bad request
    assert "price_level" in data["message"]  # Assert error mentions price_level


def test_personal_recommendation_missing_location(client):  # Test function
    payload = {  # Payload missing location
        "cuisine_preferences": ["Mexican"],
        "price_level": "Cheap",
        "desired_datetime": "2025-01-01T18:00:00",
    }
    res = client.post("api/personal/recommendation", json=payload)  # Call endpoint
    data = res.get_json()  # Parse response
    assert res.status_code == 400  # Assert bad request
    assert "location" in data["message"]  # Assert error mentions location
