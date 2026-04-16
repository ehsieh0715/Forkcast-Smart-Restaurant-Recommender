import uuid
from datetime import datetime

import pytz
from app.models import *
from app.utils.main_utils import *
from app.utils.personal_utils import *
from flask import Blueprint, jsonify, request
from sqlalchemy import func

from app import db

# Blueprint for personal-related routes
personal = Blueprint("personal", __name__)
# Timezone for New York
ny_tz = pytz.timezone("America/New_York")


# ----------------------------------------------------------------------
# Get Predicted Busyness for a Specific Restaurant (Personal)
# ----------------------------------------------------------------------
@personal.route("/personal/restaurant/<restaurant_id>/prediction", methods=["GET"])
def restaurant_prediction(restaurant_id):
    """
    Retrieve a predicted busyness level for a specific restaurant at a given time.

    Description:
        - This endpoint returns the predicted busyness level for the given restaurant_id.
        - A datetime can be supplied via query parameter; if not provided, the current time is used.
        - The endpoint ensures the closest prediction is within 4 hours of the requested time.

    Request (GET):
        URL parameter:
            restaurant_id = <UUID string of the restaurant>
        Optional query parameter:
            datetime = <ISO 8601 datetime string>
            (If not provided, current time is used.)

    Response (JSON):
        {
            "restaurant_id": "<UUID string>",
            "grid_id": <int>,
            "datetime": "<ISO 8601 datetime string>",
            "predicted_level": <float>
        }
    """
    # Parse optional datetime from query parameters
    datetime_str = request.args.get("datetime")
    if datetime_str:
        try:
            datetime_input = datetime.fromisoformat(
                datetime_str
            )  # Convert string to datetime
        except ValueError:
            return (
                jsonify({"status": "error", "message": "Invalid datetime format"}),
                400,
            )
    else:
        datetime_input = datetime.now(ny_tz)  # Use current time if not provided

    try:
        # Convert restaurant_id to UUID
        restaurant_uuid = uuid.UUID(restaurant_id)
    except ValueError:
        return (
            jsonify({"status": "error", "message": "Invalid restaurant_id format"}),
            400,
        )

    # Retrieve restaurant from database
    restaurant = (
        db.session.query(Restaurant).filter_by(restaurant_id=restaurant_uuid).first()
    )
    if not restaurant:
        return jsonify({"status": "error", "message": "Restaurant not found"}), 404

    # Query closest prediction for this restaurant's grid_id
    prediction = (
        db.session.query(BusynessPrediction)
        .filter(BusynessPrediction.grid_id == restaurant.grid_id)
        .order_by(
            func.abs(
                func.extract("epoch", BusynessPrediction.timestamp - datetime_input)
            )
        )
        .first()
    )

    # Handle missing prediction
    if not prediction:
        return jsonify({"status": "error", "message": "No prediction data found"}), 404

    # Validate that prediction timestamp is within 4 hours of requested datetime
    max_time_diff_seconds = 3600 * 4
    time_diff_seconds = abs((prediction.timestamp - datetime_input).total_seconds())
    if time_diff_seconds > max_time_diff_seconds:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "No prediction data close to requested datetime",
                }
            ),
            404,
        )

    # Return prediction details
    return (
        jsonify(
            {
                "restaurant_id": str(restaurant.restaurant_id),
                "grid_id": prediction.grid_id,
                "datetime": prediction.timestamp.isoformat(),
                "predicted_level": round(prediction.predicted_level, 2),
            }
        ),
        200,
    )


# ----------------------------------------------------------------------
# Get Personal Restaurant Recommendations
# ----------------------------------------------------------------------
@personal.route("/personal/recommendation", methods=["POST"])
def personal_recommendation():
    """
    Retrieve personalized restaurant recommendations based on user preferences and a target time.

    Description:
        - This endpoint calculates a ranked list of restaurant recommendations for a single user.
        - A desired datetime can be provided to retrieve busyness predictions closest to that time.
        - For each candidate restaurant, the system queries the BusynessPrediction table and selects
          the prediction with the timestamp closest to the desired datetime.
        - Only predictions within 4 hours of the requested time are considered.
        - Results are scored using a personal fit score algorithm and sorted by fit score (highest first),
          with a maximum of 100 results returned.

    Request (POST, JSON):
        {
            "location": {
                "latitude": <float>,    # required
                "longitude": <float>    # required
            },
            "cuisine_preferences": <list of strings, or comma-separated string, or {cuisine: weight}>,
            "price_level": "Cheap" | "Medium" | "Expensive",  # required
            "desired_datetime": "<ISO 8601 datetime string>", # optional, defaults to current NY time
            "rating": <float minimum rating>,                 # optional
            "review_count": <int minimum review count>,       # optional
            "busyness_level_max": <int max busyness level>,   # optional
            "busyness_preference": <int weighting preference> # optional, default 3
        }

    Response (JSON):
        {
            "recommendations": [
                {
                    "restaurant_id": "<UUID string>",
                    "name": "<string>",
                    "cuisine": "<string>",
                    "predicted_busyness": <float>,
                    "timestamp": "<ISO 8601 datetime string>",  # timestamp of the closest prediction
                    "price_level": <int>,
                    "rating": <float or null>,
                    "review_count": <int or null>,
                    "distance_meters": <int>,
                    "fit_score": <float>,
                    "image_url": "<string or null>"
                },
                ...
            ]
        }
    """
    data = request.get_json() or {}

    # ----------------------------
    # Validate presence of location
    # ----------------------------
    location = data.get("location")
    if not location:
        return jsonify({"status": "error", "message": "Missing location data"}), 400

    user_lat = location.get("latitude") or location.get("lat")
    user_lon = location.get("longitude") or location.get("lon")
    print(f"[DEBUG] Received location: lat={user_lat}, lon={user_lon}")
    if user_lat is None or user_lon is None:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Missing or incomplete location coordinates",
                }
            ),
            400,
        )

    # ----------------------------
    # Parse cuisine preferences
    # ----------------------------
    cuisine_preferences = data.get("cuisine_preferences")
    if isinstance(cuisine_preferences, list):
        cuisine_list = []
        for item in cuisine_preferences:
            if not isinstance(item, str):
                return (
                    jsonify(
                        {"status": "error", "message": "Each cuisine must be a string"}
                    ),
                    400,
                )
            cuisine_list.extend([c.strip() for c in item.split(",") if c.strip()])
        cuisine_preferences = {c.lower(): 1.0 for c in cuisine_list}
    elif isinstance(cuisine_preferences, str):
        cuisine_list = [c.strip() for c in cuisine_preferences.split(",") if c.strip()]
        cuisine_preferences = {c.lower(): 1.0 for c in cuisine_list}
    elif isinstance(cuisine_preferences, dict):
        cuisine_preferences = {
            str(k).lower(): float(v) for k, v in cuisine_preferences.items()
        }
    else:
        return (
            jsonify(
                {"status": "error", "message": "Invalid format for cuisine_preferences"}
            ),
            400,
        )

    # ----------------------------
    # Parse price level
    # ----------------------------
    price_map = {"Cheap": 1, "Medium": 2, "Expensive": 3}
    price_level_str = data.get("price_level")
    if price_level_str not in price_map:
        return (
            jsonify({"status": "error", "message": "Missing or invalid price_level"}),
            400,
        )
    price_level = price_map[price_level_str]

    # ----------------------------
    # Parse desired datetime
    # ----------------------------
    desired_datetime_str = data.get("desired_datetime")
    if desired_datetime_str:
        try:
            desired_datetime = datetime.fromisoformat(desired_datetime_str)
        except ValueError:
            return (
                jsonify(
                    {"status": "error", "message": "Invalid desired_datetime format"}
                ),
                400,
            )
    else:
        desired_datetime = datetime.now(ny_tz)

    # ----------------------------
    # Optional filters
    # ----------------------------
    rating = data.get("rating", None)
    review_count = data.get("review_count", None)
    busyness_max = data.get("busyness_level_max", None)
    busyness_preference = data.get("busyness_preference", 3)

    # ----------------------------
    # Retrieve candidate restaurants
    # ----------------------------
    candidates = get_filtered_candidates(
        price_level=price_level,
        cuisine_keyword=None,
        min_rating=rating,
        min_reviews=review_count,
        inspection_grade=None,
        user_lat=user_lat,
        user_lon=user_lon,
        max_distance_m=1000.0 # 1 km radius for NYC

    )

    recommendations = []
    for r in candidates:
        # fetch closest prediction for this restaurant
        prediction = (
            db.session.query(BusynessPrediction)
            .filter(BusynessPrediction.grid_id == r.grid_id)
            .order_by(
                func.abs(
                    func.extract(
                        "epoch", BusynessPrediction.timestamp - desired_datetime
                    )
                )
            )
            .first()
        )

        if not prediction:
            continue

        # Optional max-busyness filter
        if busyness_max is not None and prediction.predicted_level > int(busyness_max):
            continue

        # Check that prediction is reasonably close (e.g., within 4 hours)
        time_diff_seconds = abs(
            (prediction.timestamp - desired_datetime).total_seconds()
        )
        if time_diff_seconds > 14400:  # 4 hours in seconds
            continue

        # Calculate personal fit score
        final_score, distance_meters = calculate_personal_fit_score(
            r,
            prediction,
            cuisine_preferences,
            user_lat,
            user_lon,
            busyness_preference,
            price_level,
            rating if rating is not None else 0.0,
        )

        recommendations.append(
            {
                "restaurant_id": str(r.restaurant_id),
                "name": r.google_name or r.full_name,
                "cuisine": r.cuisine_type,
                "predicted_busyness": round(prediction.predicted_level, 2),
                "timestamp": prediction.timestamp.isoformat(),
                "price_level": r.price_level,
                "rating": round(r.rating, 2) if r.rating else None,
                "review_count": r.review_count if r.review_count else None,
                "distance_meters": int(distance_meters),
                "fit_score": round(final_score, 3),
                "image_url": r.image_url or None,
            }
        )

    # Sort by fit_score and limit
    recommendations.sort(key=lambda x: x["fit_score"], reverse=True)
    recommendations = recommendations[:100]

    return jsonify({"recommendations": recommendations}), 200
