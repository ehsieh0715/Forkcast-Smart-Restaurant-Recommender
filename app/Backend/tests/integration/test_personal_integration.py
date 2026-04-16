import uuid  # UUID for generating test IDs
from datetime import datetime, timedelta, timezone  # Date/time utilities
from urllib.parse import quote  # Encode query parameters

import pytest  # Pytest for fixtures and test execution
from app.models import BusynessPrediction  # Import models used in tests
from app.models import Restaurant

from app import create_app, db  # Import app factory and database instance

# ----------------------------------------------
# Fixtures
# ----------------------------------------------


@pytest.fixture
def app_instance():
    """Create a Flask app instance in testing mode and manage DB lifecycle."""
    app = create_app(testing=True)  # Create app with testing configuration
    with app.app_context():  # Push app context
        db.create_all()  # Create all tables
        yield app  # Yield the app instance to the tests
        db.session.remove()  # Clean up DB session
        db.drop_all()  # Drop all tables after tests complete


@pytest.fixture
def client(app_instance):
    """Provide a test client for making API calls."""
    return app_instance.test_client()  # Return the Flask test client


@pytest.fixture
def sample_prediction(app_instance):
    """Seed a sample prediction for tests requiring busyness data."""
    with app_instance.app_context():  # Push app context
        pred = BusynessPrediction(  # Create prediction entry
            grid_id="grid-001",
            predicted_level=4.0,
            timestamp=datetime.now(timezone.utc).replace(microsecond=0),
        )
        db.session.add(pred)  # Add to session
        db.session.commit()  # Commit changes
        yield pred  # Yield prediction to dependent tests


@pytest.fixture
def sample_restaurant(app_instance, sample_prediction):
    """Seed a sample restaurant linked to the sample prediction."""
    with app_instance.app_context():  # Push app context
        rest = Restaurant(  # Create a restaurant entry
            place_id="sample-place-id",
            full_name="Sample Restaurant",
            address="123 Sample St",
            rating=4.0,
            review_count=50,
            cuisine_type="Italian",
            cuisine_keyword="pizza",
            inspection_grade="A",
            lat=40.7128,
            lon=-74.0060,
            phone="123-456-7890",
            image_url="http://example.com/sample.jpg",
            google_name="Sample Google Name",
            grid_id=sample_prediction.grid_id,
        )
        db.session.add(rest)  # Add to session
        db.session.commit()  # Commit to DB
        yield rest  # Yield restaurant for tests


# ----------------------------------------------
# Tests for Personal Routes
# ----------------------------------------------


def test_restaurant_prediction_success(client, sample_restaurant, sample_prediction):
    """Test retrieving prediction data for a valid restaurant with datetime."""
    dt = quote(
        sample_prediction.timestamp.isoformat(timespec="seconds")
    )  # Encode datetime
    response = client.get(
        f"api/personal/restaurant/{sample_restaurant.restaurant_id}/prediction?datetime={dt}"
    )
    assert response.status_code == 200  # Expect OK
    data = response.get_json()  # Parse response
    assert data["restaurant_id"] == str(sample_restaurant.restaurant_id)  # IDs match
    assert "predicted_level" in data  # Prediction field present


def test_restaurant_prediction_missing_datetime(client, sample_restaurant):
    """Test retrieving prediction without providing a datetime."""
    response = client.get(
        f"api/personal/restaurant/{sample_restaurant.restaurant_id}/prediction"
    )
    assert response.status_code == 200  # OK even without datetime
    data = response.get_json()  # Parse response
    assert data["restaurant_id"] == str(sample_restaurant.restaurant_id)  # IDs match
    assert "predicted_level" in data  # Prediction field present


def test_restaurant_prediction_invalid_datetime(client, sample_restaurant):
    """Test retrieving prediction with an invalid datetime format."""
    response = client.get(
        f"api/personal/restaurant/{sample_restaurant.restaurant_id}/prediction?datetime=not-a-date"
    )
    assert response.status_code == 400  # Expect bad request
    data = response.get_json()  # Parse response
    assert "Invalid datetime format" in data["message"]  # Check error message


def test_restaurant_prediction_invalid_uuid(client):
    """Test retrieving prediction with an invalid restaurant UUID."""
    dt = quote(
        datetime.now(timezone.utc).isoformat(timespec="seconds")
    )  # Encode current datetime
    response = client.get(
        f"api/personal/restaurant/invalid-uuid/prediction?datetime={dt}"
    )
    assert response.status_code == 400  # Expect bad request
    data = response.get_json()  # Parse response
    assert "Invalid restaurant_id format" in data["message"]  # Check error message


def test_restaurant_prediction_not_found(client):
    """Test retrieving prediction for a restaurant UUID that does not exist."""
    dt = quote(
        datetime.now(timezone.utc).isoformat(timespec="seconds")
    )  # Encode current datetime
    fake_uuid = str(uuid.uuid4())  # Generate fake UUID
    response = client.get(
        f"api/personal/restaurant/{fake_uuid}/prediction?datetime={dt}"
    )
    assert response.status_code == 404  # Expect not found
    data = response.get_json()  # Parse response
    assert "Restaurant not found" in data["message"]  # Check error message


def test_restaurant_prediction_no_data(client, sample_restaurant):
    """Test retrieving prediction where no close data is available."""
    past_dt = (datetime.now(timezone.utc) - timedelta(days=365 * 10)).replace(
        microsecond=0
    )  # Generate old datetime
    dt_str = quote(past_dt.isoformat(timespec="seconds"))  # Encode datetime
    response = client.get(
        f"api/personal/restaurant/{sample_restaurant.restaurant_id}/prediction?datetime={dt_str}"
    )
    assert response.status_code == 404  # Expect not found
    data = response.get_json()  # Parse response
    assert "No prediction data close" in data["message"]  # Check error message


def test_personal_recommendation_success(client, sample_restaurant):
    """Test getting personalized recommendations with valid payload."""
    payload = {  # Build request payload
        "location": {"latitude": 40.7128, "longitude": -74.0060},
        "cuisine_preferences": ["pizza", "Italian", "Thai"],
        "price_level": "Cheap",
        "rating": 3.0,
        "review_count": 10,
        "desired_datetime": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "busyness_level_max": 5,
        "busyness_preference": 3,
        "image_url": "http://example.com/sample.jpg",
    }
    response = client.post("api/personal/recommendation", json=payload)  # POST request
    assert response.status_code == 200  # Expect OK
    data = response.get_json()  # Parse response
    assert "recommendations" in data  # Recommendations key present
    assert isinstance(data["recommendations"], list)  # Ensure list
    if data["recommendations"]:  # If any recommendations returned
        rec = data["recommendations"][0]  # Inspect first recommendation
        assert "restaurant_id" in rec  # Check required field
        assert "fit_score" in rec  # Check fit score field


def test_personal_recommendation_missing_fields(client):
    """Test error when required fields are missing in payload."""
    payload = {  # Missing longitude and other required fields
        "location": {"latitude": 40.7128},
        "cuisine_preferences": ["pizza"],
    }
    response = client.post("api/personal/recommendation", json=payload)  # POST request
    assert response.status_code == 400  # Expect bad request
    data = response.get_json()  # Parse response
    # Message should indicate missing or incomplete location data
    assert (
        "Missing or incomplete location" in data["message"]
        or "Missing" in data["message"]
    )
