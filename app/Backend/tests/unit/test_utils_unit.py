from datetime import datetime  # datetime utilities if needed in future
from datetime import timezone
from math import isclose  # isclose for comparing floating point values

import pytest  # Pytest framework for running tests
from app.utils.group_utils import \
    calculate_group_fit_score  # function under test
from app.utils.personal_utils import (  # functions under test
    calculate_personal_fit_score, haversine_distance)

# -----------------------------
# Dummy model classes to simulate SQLAlchemy models
# -----------------------------


class DummyRestaurant:
    def __init__(self, lat, lon, cuisine_keyword=None, rating=None):
        self.lat = lat  # Latitude of the restaurant
        self.lon = lon  # Longitude of the restaurant
        self.cuisine_keyword = cuisine_keyword  # Cuisine keywords (list of dicts)
        self.rating = rating  # Restaurant rating
        self.price_level = 2  # Default price level for testing


class DummyPrediction:
    def __init__(self, predicted_level):
        self.predicted_level = predicted_level  # Predicted busyness level


# -----------------------------
# Tests for haversine_distance
# -----------------------------


def test_haversine_distance_zero():
    """Distance between identical coordinates should be zero."""
    d = haversine_distance(40.0, -73.0, 40.0, -73.0)  # Same coordinates
    assert isclose(d, 0.0, abs_tol=1e-6)  # Should be essentially zero


def test_haversine_distance_known():
    """Roughly verify distance between two known points (approx NYC to nearby)."""
    d = haversine_distance(
        40.7128, -74.0060, 40.730610, -73.935242
    )  # Two known coordinates
    # Should be around 6–8 km → 6000–8000 meters, allow range
    assert 5000 <= d <= 10000


# -----------------------------
# Tests for calculate_group_fit_score
# -----------------------------


def test_calculate_group_fit_score_perfect_match():
    # Create a dummy restaurant with ideal match attributes
    r = DummyRestaurant(
        lat=40.0,
        lon=-73.0,
        cuisine_keyword=[{"title": "italian"}],  # Matches preference
        rating=5.0,
    )
    prediction = DummyPrediction(predicted_level=3)  # Balanced busyness level
    prefs = [
        {
            "cuisine_preferences": ["italian"],  # Matches the restaurant
            "distance_preference": 5,  # Close enough distance
            "busyness_preference": 3,  # Neutral busyness preference
            "minimum_rating": 4.0,  # Restaurant meets min rating
            "price_level": 2,
        }
    ]
    score, dist = calculate_group_fit_score(
        r, prediction, prefs, 40.0, -73.0
    )  # Call function under test
    assert isclose(dist, 0.0, abs_tol=1e-6)  # Distance should be zero
    assert score > 0.9  # High score expected


def test_calculate_group_fit_score_poor_match():
    # Create a dummy restaurant far away and wrong cuisine
    r = DummyRestaurant(
        lat=41.0,
        lon=-75.0,
        cuisine_keyword=[{"title": "french"}],  # Not matching preferences
        rating=2.0,  # Low rating
    )
    prediction = DummyPrediction(predicted_level=5)  # Very busy
    prefs = [
        {
            "cuisine_preferences": ["italian"],  # Mismatch
            "distance_preference": 1,  # User wants close but it's far
            "busyness_preference": 1,  # User wants low busyness
            "minimum_rating": 4.0,  # Restaurant does not meet
            "price_level": 1,  # User wants cheap
        }
    ]
    score, dist = calculate_group_fit_score(r, prediction, prefs, 40.0, -73.0)
    assert dist > 100000  # Very far distance
    assert score < 0.6  # Poor match expected


# -----------------------------
# Tests for calculate_personal_fit_score
# -----------------------------


def test_calculate_personal_fit_score_good_match():
    # Create a dummy restaurant with ideal match attributes
    r = DummyRestaurant(
        lat=40.0,
        lon=-73.0,
        cuisine_keyword=[{"title": "italian"}],  # Matches preferences
    )
    prediction = DummyPrediction(predicted_level=3)  # Moderate busyness
    cuisine_prefs = {"italian": 1.0}  # User loves Italian
    score, dist = calculate_personal_fit_score(
        r,
        prediction,
        cuisine_prefs,
        40.0,
        -73.0,
        busyness_preference=3,  # Neutral busyness
        price_preference=2,  # Matches default price
        minimum_rating=4.0,  # Restaurant rating would need to meet
    )
    assert isclose(dist, 0.0, abs_tol=1e-6)  # Should be zero distance
    assert score > 0.8  # Should be a good match


def test_calculate_personal_fit_score_bad_match():
    # Create a dummy restaurant far away and wrong cuisine
    r = DummyRestaurant(
        lat=42.0, lon=-75.0, cuisine_keyword=[{"title": "thai"}]  # Different cuisine
    )
    prediction = DummyPrediction(predicted_level=5)  # Very busy
    cuisine_prefs = {"italian": 1.0}  # User prefers Italian
    score, dist = calculate_personal_fit_score(
        r,
        prediction,
        cuisine_prefs,
        40.0,
        -73.0,
        busyness_preference=1,  # Prefers low busyness
        price_preference=3,  # Prefers different price
        minimum_rating=4.0,  # Restaurant might not meet
    )
    assert dist > 200000  # Very far distance
    assert score < 0.4  # Low score expected
