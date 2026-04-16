# app/Backend/tests/unit/test_models_unit.py

import uuid
from datetime import datetime, timezone

import pytest
from app.models import *


# ==== User ====
def test_user_model():
    user = User(
        user_id=uuid.uuid4(),
        name="Alice Smith",
        username="alice123",
        email="alice@example.com",
        password_hash="hashedpass123",
        latitude=40.7128,
        longitude=-74.0060,
    )
    assert user.username == "alice123"
    assert repr(user) == f"<{user.name}, is {user.username}>"


# ==== Restaurant ====
def test_restaurant_model():
    restaurant = Restaurant(
        restaurant_id=uuid.uuid4(),
        place_id="abc123",
        full_name="Mama's Kitchen",
        lat=40.7128,
        lon=-74.0060,
        cuisine_type="Italian",
        rating=4.5,
        review_count=200,
    )
    assert restaurant.full_name == "Mama's Kitchen"
    assert repr(restaurant) == f"<Restaurant {restaurant.full_name}>"


# ==== Group ====
def test_group_model():
    group = Group(
        group_id=uuid.uuid4(),
        group_name="Brunch Squad",
        created_by=uuid.uuid4(),
        members_json={"u1": {"rating": 4.5}},
    )
    assert group.group_name == "Brunch Squad"
    assert isinstance(group.members_json, dict)
    assert repr(group).startswith("<Group")


# ==== BusynessPrediction ====
def test_busyness_prediction_model():
    prediction = BusynessPrediction(
        grid_id="grid1", timestamp=datetime.now(timezone.utc), predicted_level=3
    )
    assert prediction.grid_id == "grid1"
    assert isinstance(prediction.predicted_level, int)
    assert repr(prediction).startswith("<BusynessPrediction")


# ==== GroupFitScore ====
def test_group_fit_score_model():
    score = GroupFitScore(
        score_id=uuid.uuid4(),
        group_id=uuid.uuid4(),
        restaurant_id=uuid.uuid4(),
        fit_score=0.92,
        fit_breakdown={"busyness": 0.5, "distance": 0.4},
    )
    assert isinstance(score.fit_score, float)
    assert score.fit_score <= 1.0
    assert repr(score).startswith("<FitScore")


# ==== PersonalFitScore ====
def test_personal_fit_score_model():
    score = PersonalFitScore(
        score_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        restaurant_id=uuid.uuid4(),
        fit_score=0.88,
        fits_breakdown={"cuisine": 0.9},
    )
    assert isinstance(score.fit_score, float)
    assert isinstance(score.fits_breakdown, dict)


# ==== ComparisonSession ====
def test_comparison_session_model():
    session = ComparisonSession(
        session_id=uuid.uuid4(),
        created_at=datetime.now(timezone.utc),
        restaurants_json=["abc", "def"],
    )
    assert isinstance(session.restaurants_json, list)
    assert repr(session).startswith("<ComparisonSession")


# ==== LocationMapping ====
def test_location_mapping_model():
    mapping = LocationMapping(main_location="Central", geometry="POLYGON((...))")
    assert mapping.main_location == "Central"


# ==== GridInfo ====
def test_grid_info_model():
    info = GridInfo(
        grid_id="grid-42",
        lat=40.7,
        lon=-74.0,
        geometry="POLYGON((...))",
        restaurant_count=100,
        population=2000,
    )
    assert info.grid_id == "grid-42"
    assert info.restaurant_count == 100


# ==== Holiday ====
def test_holiday_model():
    h = Holiday(holiday_date=datetime(2025, 12, 25).date())
    assert h.holiday_date.year == 2025


# ==== RestaurantPopularHour ====
def test_popular_hour_model():
    rph = RestaurantPopularHour(place_id="abc123", day="Monday", hour_12=30, hour_13=50)
    assert rph.day == "Monday"
    assert isinstance(rph.hour_12, int)


# ==== RestaurantOpeningHour ====
def test_opening_hour_model():
    roh = RestaurantOpeningHour(
        restaurant_id=uuid.uuid4(),  # Use valid UUID for FK
        day="Monday",
        hour_9=True,
        hour_10=False,
    )
    assert roh.day == "Monday"
    assert roh.hour_9 is True


# ==== LatestGridBusyness ====
def test_latest_grid_busyness_model():
    busyness = LatestGridBusyness(
        grid_id="grid-007",
        predicted_level=4,
        timestamp=datetime.now(timezone.utc),
        geometry="POLYGON((...))",
    )
    assert busyness.predicted_level == 4
    assert repr(busyness).startswith("<LatestGridBusyness")
