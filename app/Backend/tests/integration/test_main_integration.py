import json  # For parsing response data
import os  # For file paths
from datetime import datetime, timezone  # For timestamps

import pytest  # Import pytest for fixtures and tests
from app.models import BusynessPrediction  # Import models used in tests
from app.models import Restaurant
from dotenv import load_dotenv  # Load environment variables from .env
from shapely.geometry import Polygon  # For creating and validating geometry
from shapely.geometry import shape
from shapely.wkb import \
    dumps as wkb_dumps  # For writing geometry to WKB format
from sqlalchemy import text  # For raw SQL execution

from app import create_app, db  # Import Flask app factory and database

# Load the test-specific environment variables
env_path = os.path.join(os.path.dirname(__file__), ".env.test")  # Path to test .env
load_dotenv(dotenv_path=env_path, override=True)  # Load and override env variables

# ----------------------------------------------
# Fixtures
# ----------------------------------------------


@pytest.fixture
def app_instance():
    """Create and configure a Flask app instance for testing."""
    app = create_app(testing=True)  # Create the app in testing mode
    with app.app_context():  # Push an application context
        db.create_all()  # Create all tables
        yield app  # Yield app instance to tests
        db.session.remove()  # Remove session after tests
        db.drop_all()  # Drop tables after tests


@pytest.fixture
def client(app_instance):
    """Return a test client for sending requests to the app."""
    return app_instance.test_client()  # Create and return test client


@pytest.fixture
def test_data(app_instance):
    """Seed a test prediction and restaurant in the database."""
    with app_instance.app_context():  # Push an application context
        prediction = BusynessPrediction(  # Create a prediction entry
            grid_id="G-001", predicted_level=2, timestamp=datetime.now(timezone.utc)
        )
        db.session.add(prediction)  # Add prediction to session
        db.session.commit()  # Commit to save prediction

        restaurant = Restaurant(  # Create a restaurant entry
            place_id="place123",
            full_name="Mock Restaurant",
            address="1 Main St",
            lat=40.7128,
            lon=-74.0060,
            phone="000-000-0000",
            rating=4.5,
            review_count=120,
            cuisine_type="Thai",
            cuisine_keyword="thai",
            inspection_grade="A",
            image_url="http://mock.com/img.jpg",
            google_name="Mock Google Name",
            grid_id="G-001",
        )
        db.session.add(restaurant)  # Add restaurant to session
        db.session.commit()  # Commit to save restaurant

        yield restaurant  # Yield seeded restaurant to tests


# ----------------------------------------------
# Tests for Main Routes
# ----------------------------------------------


def test_root_route(client):
    """Test that the root route returns a running message."""
    res = client.get("api/")  # Send GET request
    assert res.status_code == 200  # Expect OK status
    assert res.get_json()["message"].startswith("Restaurant Busyness")  # Message check


def test_healthcheck(client):
    """Test that the healthcheck endpoint returns OK."""
    res = client.get("api/healthcheck")  # Send GET request
    assert res.status_code == 200  # Expect OK status
    assert res.get_json()["status"] == "ok"  # Status field check


def test_list_all_restaurants(client, test_data):
    """Test listing all restaurants returns seeded data."""
    res = client.get("api/restaurants")  # GET all restaurants
    assert res.status_code == 200  # Expect OK status
    data = res.get_json()  # Parse JSON response
    assert data["status"] == "success"  # Status field check
    assert any(
        r["full_name"] == "Mock Restaurant" for r in data["restaurants"]
    )  # Restaurant present


def test_get_single_restaurant_details(client, test_data):
    """Test retrieving details of a single restaurant."""
    res = client.get(
        f"api/restaurants/{test_data.restaurant_id}"
    )  # GET specific restaurant
    assert res.status_code == 200  # Expect OK status
    data = res.get_json()  # Parse response
    assert data["full_name"] == "Mock Restaurant"  # Name matches
    assert str(data["restaurant_id"]) == str(test_data.restaurant_id)  # ID matches
    assert "predicted_level" in data  # Predicted level included


def test_get_restaurant_busyness(client, test_data):
    """Test retrieving busyness level for a restaurant."""
    res = client.get(
        f"api/restaurants/{test_data.restaurant_id}/busyness"
    )  # GET busyness
    assert res.status_code == 200  # Expect OK status
    data = res.get_json()  # Parse response
    assert data["full_name"] == "Mock Restaurant"  # Name matches
    assert data["restaurant_id"] == str(test_data.restaurant_id)  # ID matches
    assert "predicted_level" in data  # Busyness prediction included


def test_get_all_predictions(client, test_data):
    """Test retrieving predictions for all restaurants."""
    res = client.get("api/restaurants/predictions")  # GET predictions
    assert res.status_code == 200  # Expect OK status
    data = res.get_json()  # Parse response
    assert data["status"] == "success"  # Status check
    assert any(
        p["restaurant_full_name"] == "Mock Restaurant" for p in data["predictions"]
    )  # Restaurant in predictions
    assert all("restaurant_id" in p for p in data["predictions"])  # IDs included


def test_heatmap_route_returns_geojson(client):
    """Test that heatmap route returns valid GeoJSON."""
    polygon = Polygon(
        [  # Create a polygon shape
            (-74.01, 40.71),
            (-74.00, 40.71),
            (-74.00, 40.72),
            (-74.01, 40.72),
            (-74.01, 40.71),
        ]
    )
    geometry_wkb = wkb_dumps(polygon)  # Convert polygon to WKB
    timestamp = datetime.now(timezone.utc)  # Get current timestamp
    # Insert grid info directly via SQL
    db.session.execute(
        text(
            """
        INSERT INTO grid_info (grid_id, lat, lon, geometry, restaurant_count, population)
        VALUES (:grid_id, :lat, :lon, ST_GeomFromWKB(:geometry, 4326), :rcount, :pop)
    """
        ),
        {
            "grid_id": "TEST-GRID-1",
            "lat": 40.71,
            "lon": -74.00,
            "geometry": geometry_wkb,
            "rcount": 1,
            "pop": 100,
        },
    )
    # Insert a prediction for that grid
    db.session.execute(
        text(
            """
        INSERT INTO busyness_predictions (grid_id, timestamp, predicted_level)
        VALUES (:grid_id, :timestamp, :predicted_level)
    """
        ),
        {"grid_id": "TEST-GRID-1", "timestamp": timestamp, "predicted_level": 3},
    )
    db.session.commit()  # Commit both inserts
    response = client.get("api/heatmap")  # GET heatmap
    assert response.status_code == 200  # Expect OK
    data = json.loads(response.data)  # Parse JSON
    assert "type" in data and data["type"] == "FeatureCollection"  # Type check
    assert "features" in data  # Features key present
    assert isinstance(data["features"], list)  # Features is list
    assert len(data["features"]) > 0  # At least one feature
    feature = data["features"][0]  # Take first feature
    assert "geometry" in feature  # Geometry present
    assert "properties" in feature  # Properties present
    props = feature["properties"]  # Get properties dict
    assert "grid_id" in props and props["grid_id"] == "TEST-GRID-1"  # Grid ID matches
    assert "predicted_level" in props and props["predicted_level"] == 3  # Level matches
    assert "timestamp" in props  # Timestamp present
    geom = feature["geometry"]  # Get geometry
    assert geom["type"] == "Polygon"  # Geometry is polygon
    parsed_geom = shape(geom)  # Parse geometry
    assert parsed_geom.geom_type == "Polygon"  # Confirm shape type


def test_get_filter_options(client, test_data):
    """Test retrieving available filter options."""
    res = client.get("api/filters/options")  # GET filter options
    assert res.status_code == 200  # Expect OK
    data = res.get_json()  # Parse response
    assert data["status"] == "success"  # Status check
    assert "cuisine_types" in data["filters"]  # Check cuisine_types key
    assert "Thai" in data["filters"]["cuisine_types"]  # Ensure seeded cuisine appears
