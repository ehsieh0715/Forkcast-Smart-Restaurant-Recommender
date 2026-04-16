import re
from math import atan2, cos, radians, sin, sqrt
from typing import Dict, List, Tuple

from app.models import BusynessPrediction, Restaurant
from app.utils.main_utils import haversine_distance
from sqlalchemy import func

from app import db


def calculate_personal_fit_score(
    r,
    prediction,
    cuisine_preferences: Dict[str, float],
    user_lat: float,
    user_lon: float,
    busyness_preference: int,
    price_preference: int,
    minimum_rating: float,
) -> Tuple[float, float]:
    """
    Calculate the fit score between a restaurant and the user's preferences.

    Factors:
        - Distance from user (closer = higher score)
        - Busyness level vs user preference
        - Cuisine match
        - Price level match
        - Rating minimum

    Returns:
        (final_score: float, distance_meters: float)
    """

    # -----------------------
    # DISTANCE FACTOR
    # -----------------------
    distance_meters = haversine_distance(user_lat, user_lon, r.lat, r.lon)
    distance_score = max(0.0, 1.0 - (distance_meters / 1000.0))  # normalize over 1 km

    # -----------------------
    # BUSYNESS FACTOR
    # -----------------------
    predicted_busyness = (prediction.predicted_level - 1) / 4.0  # normalize 1–5 to 0–1
    busyness_target = (busyness_preference - 1) / 4.0
    busyness_score = 1.0 - abs(predicted_busyness - busyness_target)

    # -----------------------
    # CUISINE FACTOR (YES/NO)
    # -----------------------
    restaurant_cuisine_data = r.cuisine_keyword or []  # fallback to empty list
    if not isinstance(restaurant_cuisine_data, list):
        # If data is somehow not a list, log it and ignore
        print(f"[DEBUG] Restaurant {r.full_name} has invalid cuisine_keyword type: {type(restaurant_cuisine_data)}")
        restaurant_cuisine_data = []

    restaurant_cuisines = []
    for c in restaurant_cuisine_data:
        if isinstance(c, dict) and "title" in c and isinstance(c["title"], str):
            restaurant_cuisines.append(c["title"].strip().lower())
    user_cuisine_prefs = {k.lower() for k in cuisine_preferences.keys()}
    cuisine_score = (
        1.0 if any(c in user_cuisine_prefs for c in restaurant_cuisines) else 0.0
    )

    # -----------------------
    # PRICE LEVEL FACTOR
    # -----------------------
    if r.price_level is None:
        price_score = 0.0
    else:
        diff = abs(r.price_level - price_preference)
        price_score = 1.0 - min(diff / 2.0, 1.0)

    # -----------------------
    # RATING FACTOR
    # -----------------------
    if r.rating is None:
        rating_score = 0.0
    else:
        if r.rating < minimum_rating:
            rating_score = 1.0 - min((minimum_rating - r.rating) / 5.0, 1.0)
        else:
            rating_score = 1.0

    # -----------------------
    # FINAL WEIGHTED SCORE
    # -----------------------
    final_score = (
        0.40 * cuisine_score
        + 0.20 * distance_score
        + 0.15 * busyness_score
        + 0.10 * rating_score
        + 0.15 * price_score
    )

    final_score = max(0.0, min(1.0, final_score))
    return final_score, distance_meters

# filters restaurants based on optional parameters
def get_filtered_candidates(
    cuisine_keyword: str = None,
    min_rating: float = None,
    min_reviews: int = None,
    inspection_grade: str = None,
    price_level: int = None,
    user_lat: float = None,
    user_lon: float = None,
    max_distance_m: float = 3000.0,  # 3 km radius for NYC
) -> List[Restaurant]:
    """
    Queries restaurants based on optional filters and filters by distance if lat/lon provided.
    """
    query = db.session.query(Restaurant)

    # Static filters
    if cuisine_keyword is not None:
        query = query.filter(Restaurant.cuisine_keyword.ilike(f"%{cuisine_keyword}%"))
    if min_rating is not None:
        query = query.filter(Restaurant.rating >= min_rating)
    if min_reviews is not None:
        query = query.filter(Restaurant.review_count >= min_reviews)
    if inspection_grade is not None:
        query = query.filter(Restaurant.inspection_grade == inspection_grade)
    if price_level is not None:
        query = query.filter(Restaurant.price_level == price_level)

    raw_results = query.all()
    print(
        f"[DEBUG] get_filtered_candidates (pre-distance) → {len(raw_results)} results"
    )

    # Distance filter
    if user_lat is not None and user_lon is not None:
        filtered_results = []
        for r in raw_results:
            if r.lat is None or r.lon is None:
                continue
            dist = haversine_distance(user_lat, user_lon, r.lat, r.lon)
            if dist <= max_distance_m:
                filtered_results.append(r)
        print(
            f"[DEBUG] get_filtered_candidates (post-distance) → {len(filtered_results)} results within {max_distance_m}m"
        )
        return filtered_results

    return raw_results


# Get the nearest busyness prediction for a restaurant based on grid_id and desired datetime
def get_nearest_prediction(grid_id, desired_datetime, max_hours=4):
    """
    Retrieves the busyness prediction nearest to the given datetime for the specified grid.
    Rejects if no prediction is within `max_hours`.
    """
    prediction = (
        db.session.query(BusynessPrediction)
        .filter(BusynessPrediction.grid_id == grid_id)
        .order_by(
            func.abs(
                func.extract("epoch", BusynessPrediction.timestamp - desired_datetime)
            )
        )
        .first()
    )
    if not prediction:
        return None

    # Enforce max distance threshold
    time_diff = abs((prediction.timestamp - desired_datetime).total_seconds())
    if time_diff > max_hours * 3600:
        return None

    return prediction


# Normalize a string by stripping whitespace and lowercasing
def normalize(text: str) -> str:
    """
    Normalizes text by stripping whitespace and lowercasing.
    """
    return re.sub(r"\s+", " ", text).strip().lower()
