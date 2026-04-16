from datetime import datetime

import pytz
from app.models import *
from app.utils.main_utils import *
from dateutil import parser
from flask import Blueprint, jsonify, request
from geoalchemy2.shape import dumps
from shapely import wkb, wkt
from shapely.geometry import mapping
from shapely.wkb import loads as wkb_loads
from sqlalchemy import func, text

from app import db

# Main Blueprint for API routes
main = Blueprint("main", __name__)
# Timezone for New York
ny_tz = pytz.timezone("America/New_York")


# ----------------------------------------------------------------------
# Backend Health Check (Home)
# ----------------------------------------------------------------------
@main.route("/")
def home():
    """
    Backend health check endpoint.

    Description:
        - This endpoint serves as a simple check to confirm that the
          Restaurant Busyness Predictor backend is running and reachable.

    Request (GET):
        No parameters.

    Response (JSON):
        {
            "message": "Restaurant Busyness Predictor backend is running."
        }
    """
    # Return a simple JSON message indicating the backend is operational
    return jsonify({"message": "Restaurant Busyness Predictor backend is running."})


# ----------------------------------------------------------------------
# List All Restaurants with Predicted Busyness
# ----------------------------------------------------------------------
@main.route("/restaurants", methods=["GET"])
def list_all_restaurants():
    """
    Retrieve a list of all restaurants with their predicted busyness levels.

    Description:
        - This endpoint returns all restaurants in the database along with
          the predicted busyness level closest to a requested time.
        - If no requested_time is provided, the current time is used.

    Request (GET):
        Optional query parameter:
            requested_time = <ISO 8601 datetime string>
            (If not provided, current time is used.)

    Response (JSON):
        {
            "status": "success",
            "restaurants": [
                {
                    "restaurant_id": "<UUID string>",
                    "full_name": "<string name of restaurant>",
                    "predicted_level": <int or null>,
                    "predicted_timestamp": "<ISO 8601 datetime string or null>"
                },
                ...
            ]
        }
    """
    try:

        # Retrieve all restaurants from the database
        restaurants = db.session.query(Restaurant).all()
        restaurant_list = []

        # Build restaurant list with predicted busyness information
        for r in restaurants:
            # Append restaurant details to the list
            restaurant_list.append(
                {
                    "restaurant_id": str(r.restaurant_id),
                    "full_name": r.full_name,
                }
            )

        # Return the full list of restaurants with predictions
        return jsonify({"status": "success", "restaurants": restaurant_list}), 200

    except Exception as e:
        # Return error response (no traceback printing here, matching original)
        return jsonify({"status": "error", "message": str(e)}), 500


# ----------------------------------------------------------------------
# Get Detailed Information for a Specific Restaurant
# ----------------------------------------------------------------------
@main.route("/restaurants/<restaurant_id>", methods=["GET"])
def get_restaurant_details(restaurant_id):
    """
    Retrieve detailed information for a specific restaurant.

    Description:
        - This endpoint returns all available details for the restaurant with the given restaurant_id.
        - It also retrieves the predicted busyness level closest to a requested time.
        - If no requested_time is provided, the current time is used.

    Request (GET):
        URL parameter:
            restaurant_id = <UUID string of the restaurant>
        Optional query parameter:
            requested_time = <ISO 8601 datetime string>
            (If not provided, current time is used.)

    Response (JSON):
        {
            "restaurant_id": "<UUID>",
            "place_id": "<string>",
            "full_name": "<string>",
            "inspection_id": "<string or null>",
            "image_url": "<string or null>",
            "lat": <float>,
            "lon": <float>,
            "phone": "<string or null>",
            "rating": <float or null>,
            "review_count": <int or null>,
            "address": "<string>",
            "cuisine_type": "<string>",
            "cuisine_keyword": "<string or null>",
            "inspection_grade": "<string or null>",
            "google_name": "<string or null>",
            "restaurant_counts": <int or null>,
            "geometry": "<string or null>",
            "price_level": <int or null>,
            "lat_rounded": <float or null>,
            "lon_rounded": <float or null>,
            "grid_id": <int or null>,
            "wheelchair_friendly": <bool or null>,
            "amenities": "<string or null>",
            "opening_hours": "<string or null>",
            "predicted_level": <int or null>,
            "predicted_timestamp": "<ISO 8601 datetime string or null>"
        }
    """
    # Retrieve the restaurant object from the database
    restaurant = (
        db.session.query(Restaurant).filter_by(restaurant_id=restaurant_id).first()
    )

    # If restaurant is not found, return error
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404

    # Parse optional requested_time from query parameters
    requested_time_str = request.args.get("requested_time")
    if requested_time_str:
        requested_time = parser.isoparse(
            requested_time_str
        )  # Convert string to datetime
    else:
        requested_time = datetime.now(ny_tz)  # Use current time if not provided

    # Convert requested time to epoch seconds
    req_epoch = requested_time.timestamp()

    # Initialize predicted busyness details
    predicted_level = None
    predicted_time = None

    # Fetch the closest busyness prediction for this restaurant's grid_id
    if restaurant.grid_id:
        row = db.session.execute(
            text(
                """
            SELECT predicted_level, timestamp
            FROM busyness_predictions
            WHERE grid_id = :gid
            ORDER BY ABS(EXTRACT(EPOCH FROM timestamp) - :req_epoch)
            LIMIT 1
        """
            ),
            {"gid": restaurant.grid_id, "req_epoch": req_epoch},
        ).fetchone()

        # Populate prediction details if available
        if row:
            predicted_level = row.predicted_level
            predicted_time = row.timestamp

    # Return detailed restaurant information and prediction
    return (
        jsonify(
            {
                "restaurant_id": str(restaurant.restaurant_id),
                "place_id": restaurant.place_id,
                "full_name": restaurant.full_name,
                "inspection_id": restaurant.inspection_id,
                "image_url": restaurant.image_url,
                "lat": restaurant.lat,
                "lon": restaurant.lon,
                "phone": restaurant.phone,
                "rating": restaurant.rating,
                "review_count": restaurant.review_count,
                "address": restaurant.address,
                "cuisine_type": restaurant.cuisine_type,
                "cuisine_keyword": restaurant.cuisine_keyword,
                "inspection_grade": restaurant.inspection_grade,
                "google_name": restaurant.google_name,
                "restaurant_counts": restaurant.restaurant_counts,
                "geometry": str(restaurant.geometry) if restaurant.geometry else None,
                "price_level": restaurant.price_level,
                "lat_rounded": restaurant.lat_rounded,
                "lon_rounded": restaurant.lon_rounded,
                "grid_id": restaurant.grid_id,
                "wheelchair_friendly": restaurant.wheelchair_friendly,
                "amenities": restaurant.amenities,
                "opening_hours": restaurant.opening_hours,
                "predicted_level": predicted_level,
                "predicted_timestamp": (
                    predicted_time.isoformat() if predicted_time else None
                ),
            }
        ),
        200,
    )


# ----------------------------------------------------------------------
# Get Predicted Busyness for a Specific Restaurant
# ----------------------------------------------------------------------
@main.route("/restaurants/<restaurant_id>/busyness", methods=["GET"])
def get_restaurant_busyness(restaurant_id):
    """
    Retrieve the predicted busyness level for a specific restaurant.

    Description:
        - This endpoint returns the predicted busyness level and timestamp
          for the restaurant with the given restaurant_id.
        - If no requested_time is provided, the current time is used to find
          the closest prediction.

    Request (GET):
        URL parameter:
            restaurant_id = <UUID string of the restaurant>
        Optional query parameter:
            requested_time = <ISO 8601 datetime string>
            (If not provided, current time is used.)

    Response (JSON):
        {
            "restaurant_id": "<UUID string>",
            "full_name": "<string>",
            "grid_id": <int or null>,
            "address": "<string>",
            "predicted_level": <int or null>,
            "timestamp": "<ISO 8601 datetime string or null>"
        }
    """
    # Retrieve the restaurant from the database
    restaurant = (
        db.session.query(Restaurant).filter_by(restaurant_id=restaurant_id).first()
    )

    # If restaurant is not found, return an error
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404

    # Parse optional requested_time from query parameters
    requested_time_str = request.args.get("requested_time")
    if requested_time_str:
        requested_time = parser.isoparse(
            requested_time_str
        )  # Convert string to datetime
    else:
        requested_time = datetime.now(ny_tz)  # Use current time if not provided

    # Convert requested time to epoch seconds for querying predictions
    req_epoch = requested_time.timestamp()

    # Initialize predicted busyness details
    predicted_level = None
    predicted_time = None

    # Fetch the closest busyness prediction for this restaurant's grid_id
    if restaurant.grid_id:
        row = db.session.execute(
            text(
                """
            SELECT predicted_level, timestamp
            FROM busyness_predictions
            WHERE grid_id = :gid
            ORDER BY ABS(EXTRACT(EPOCH FROM timestamp) - :req_epoch)
            LIMIT 1
        """
            ),
            {"gid": restaurant.grid_id, "req_epoch": req_epoch},
        ).fetchone()

        # Populate prediction details if available
        if row:
            predicted_level = row.predicted_level
            predicted_time = row.timestamp

    # Return the restaurant's busyness prediction
    return jsonify(
        {
            "restaurant_id": str(restaurant.restaurant_id),
            "full_name": restaurant.full_name,
            "grid_id": restaurant.grid_id,
            "address": restaurant.address,
            "predicted_level": predicted_level,
            "timestamp": predicted_time.isoformat() if predicted_time else None,
        }
    )


# ----------------------------------------------------------------------
# Get Predicted Busyness for All Restaurants
# ----------------------------------------------------------------------
@main.route("/restaurants/predictions", methods=["GET"])
def get_all_restaurant_predictions():
    """
    Retrieve predicted busyness levels for all restaurants.

    Description:
        - This endpoint returns a list of all restaurants with their predicted
          busyness level and the timestamp of the prediction closest to a requested time.
        - If no requested_time is provided, the current time is used.

    Request (GET):
        Optional query parameter:
            requested_time = <ISO 8601 datetime string>
            (If not provided, current time is used.)

    Response (JSON):
        {
            "status": "success",
            "predictions": [
                {
                    "restaurant_id": "<UUID string>",
                    "restaurant_full_name": "<string>",
                    "predicted_busyness": <int or null>,
                    "timestamp": "<ISO 8601 datetime string or null>"
                },
                ...
            ]
        }
    """
    try:
        # Parse optional requested_time from query parameters
        requested_time_str = request.args.get("requested_time")
        if requested_time_str:
            requested_time = parser.isoparse(
                requested_time_str
            )  # Convert string to datetime
        else:
            requested_time = datetime.now(ny_tz)  # Use current time if not provided

        # Convert requested time to epoch seconds for querying predictions
        req_epoch = requested_time.timestamp()

        # Retrieve all restaurants from the database
        restaurants = db.session.query(Restaurant).all()
        prediction_list = []

        # Build a list of predictions for each restaurant
        for r in restaurants:
            predicted_level = None
            predicted_time = None

            # Fetch the closest busyness prediction for this restaurant's grid_id
            if r.grid_id:
                row = db.session.execute(
                    text(
                        """
                    SELECT predicted_level, timestamp
                    FROM busyness_predictions
                    WHERE grid_id = :gid
                    ORDER BY ABS(EXTRACT(EPOCH FROM timestamp) - :req_epoch)
                    LIMIT 1
                """
                    ),
                    {"gid": r.grid_id, "req_epoch": req_epoch},
                ).fetchone()

                # Populate prediction details if available
                if row:
                    predicted_level = row.predicted_level
                    predicted_time = row.timestamp

            # Append the prediction information to the list
            prediction_list.append(
                {
                    "restaurant_id": str(r.restaurant_id),
                    "restaurant_full_name": r.full_name,
                    "predicted_busyness": predicted_level,
                    "timestamp": predicted_time.isoformat() if predicted_time else None,
                }
            )

        # Return the predictions list
        return jsonify({"status": "success", "predictions": prediction_list}), 200

    except Exception as e:
        # Return error response (no extra logic added)
        return jsonify({"status": "error", "message": str(e)}), 500


# ----------------------------------------------------------------------
# Get Heatmap Data for Predicted Busyness
# ----------------------------------------------------------------------
@main.route("/heatmap", methods=["GET"])
def get_heatmap_data():
    """
    Retrieve heatmap data of predicted busyness levels.

    Time handling:
        - Assumes `requested_time` passed in (or default) is already in the same timezone
          as stored in the database, so no conversion is performed.

    Request (GET):
        Optional query parameter:
            requested_time = <ISO 8601 datetime string>
            (If not provided, current UTC time is used.)

    Response (JSON):
        {
            "type": "FeatureCollection",
            "features": [
                {
                    "properties": {
                        "grid_id": <int>,
                        "predicted_level": <int>,
                        "timestamp": "<ISO 8601 datetime string or null>"
                    },
                    "geometry": {
                        ...GeoJSON geometry...
                    }
                },
                ...
            ]
        }
    """
    try:
        # --- Parse optional requested_time from query parameters ---
        requested_time_str = request.args.get("requested_time")
        if requested_time_str:
            requested_time = parser.isoparse(requested_time_str)  # no tz conversion
        else:
            # use UTC or server-local depending on your storage convention
            requested_time = datetime.utcnow()

        # Convert requested time to epoch seconds for querying predictions
        req_epoch = requested_time.timestamp()

        # Optimized SQL using DISTINCT ON (leverages indexes)
        sql = text(
            """
            SELECT DISTINCT ON (bp.grid_id)
                   bp.grid_id,
                   bp.timestamp,
                   bp.predicted_level,
                   gi.geometry
            FROM busyness_predictions bp
            JOIN grid_info gi
              ON bp.grid_id = gi.grid_id
            ORDER BY bp.grid_id, ABS(EXTRACT(EPOCH FROM bp.timestamp) - :req_epoch)
        """
        )

        rows = db.session.execute(sql, {"req_epoch": req_epoch}).fetchall()

        # Build GeoJSON features list
        features = []
        for row in rows:
            if not row.geometry:
                continue  # skip missing geometry

            try:
                polygon = wkb.loads(bytes.fromhex(row.geometry))
                geojson_geom = mapping(polygon)
            except Exception:
                continue  # skip invalid geometry

            features.append(
                {
                    "type": "Feature",
                    "properties": {
                        "grid_id": row.grid_id,
                        "predicted_level": int(row.predicted_level),
                        "timestamp": (
                            row.timestamp.isoformat() if row.timestamp else None
                        ),
                    },
                    "geometry": geojson_geom,
                }
            )

        return jsonify({"type": "FeatureCollection", "features": features}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ----------------------------------------------------------------------
# Get Filter Options for Restaurant Search
# ----------------------------------------------------------------------
@main.route("/filters/options", methods=["GET"])
def get_filter_options():
    """
    Retrieve available filter options for restaurant search.

    Description:
        - This endpoint returns static and dynamic filter options that can be used
          in the application to refine restaurant search results.
        - Cuisine types are dynamically derived from the database.
        - Other filters (price levels, busyness levels, ratings, etc.) are predefined.

    Request (GET):
        No parameters.

    Response (JSON):
        {
            "status": "success",
            "filters": {
                "ratings": [1, 2, 3, 4, 5],
                "review_counts": ["0+", "10", "25+", "50+", "75+", "100+"],
                "cuisine_types": ["Italian", "Chinese", ...],
                "price_levels": ["Cheap", "Medium", "Expensive"],
                "busyness_levels": ["Low", "Medium", "High"],
                "distance_options": ["Within 500m", "Within 1km", "Within 5km", "Within 10km"]
            }
        }
    """
    try:
        # Query all cuisine_type values from Restaurant table
        cuisines_query = db.session.query(Restaurant.cuisine_type).all()
        flat_cuisines = set()

        # Flatten and clean cuisine strings
        for cuisine_str in cuisines_query:
            if cuisine_str[0]:
                flat_cuisines.update([c.strip() for c in cuisine_str[0].split(",")])

        # Sort cuisine types and provide fallback if empty
        cuisine_types = sorted(list(flat_cuisines)) or ["No Cuisines Available"]

        # Define other static filter options
        price_levels = ["Cheap", "Medium", "Expensive"]
        busyness_levels = ["Low", "Medium", "High"]
        ratings = [1, 2, 3, 4, 5]
        review_counts = ["0+", "10", "25+", "50+", "75+", "100+"]
        distance_options = ["Within 500m", "Within 1km", "Within 5km", "Within 10km"]

        # Construct final filter options object
        filter_options = {
            "ratings": ratings,
            "review_counts": review_counts,
            "cuisine_types": cuisine_types,
            "price_levels": price_levels,
            "busyness_levels": busyness_levels,
            "distance_options": distance_options,
        }

        # Return the filter options
        return jsonify({"status": "success", "filters": filter_options}), 200

    except Exception as e:
        # Return error response
        return jsonify({"status": "error", "message": str(e)}), 500


# ----------------------------------------------------------------------
# Get Top 25 Rated Restaurants with Predicted Busyness
# ----------------------------------------------------------------------
@main.route("/restaurants/top-rated", methods=["GET"])
def get_top25_rated_restaurants():
    """
    Retrieve the top 25 rated restaurants with predicted busyness data.

    Description:
        - This endpoint returns the 25 restaurants with the highest ratings
          (and review counts > 0), sorted by rating and then review count.
        - For each restaurant, the predicted busyness level closest to a
          requested time is included.
        - If no requested_time is provided, the current time is used.

    Request (GET):
        Optional query parameter:
            requested_time = <ISO 8601 datetime string>
            (If not provided, current time is used.)

    Response (JSON):
        {
            "status": "success",
            "count": <integer>,
            "restaurants": [
                {
                    "restaurant_id": "<UUID>",
                    "place_id": "<string>",
                    "full_name": "<string>",
                    "inspection_id": "<string or null>",
                    "image_url": "<string or null>",
                    "lat": <float>,
                    "lon": <float>,
                    "phone": "<string or null>",
                    "rating": <float or null>,
                    "review_count": <int>,
                    "address": "<string>",
                    "cuisine_type": "<string>",
                    "cuisine_keyword": "<string or null>",
                    "inspection_grade": "<string or null>",
                    "google_name": "<string or null>",
                    "restaurant_counts": <int or null>,
                    "geometry": "<string or null>",
                    "price_level": <int or null>,
                    "lat_rounded": <float or null>,
                    "lon_rounded": <float or null>,
                    "grid_id": <int or null>,
                    "wheelchair_friendly": <bool or null>,
                    "amenities": "<string or null>",
                    "predicted_level": <int or null>,
                    "predicted_time": "<ISO 8601 datetime or null>",
                    "opening_hours": "<string or null>"
                },
                ...
            ]
        }
    """
    try:
        # Parse optional requested_time from query parameters
        requested_time_str = request.args.get("requested_time")
        if requested_time_str:
            requested_time = parser.isoparse(
                requested_time_str
            )  # Convert string to datetime
        else:
            requested_time = datetime.now(ny_tz)  # Use current time if not provided

        # Convert requested time to epoch seconds for querying predictions
        req_epoch = requested_time.timestamp()

        # Query top 25 restaurants by rating and review count
        top_restaurants = (
            db.session.query(Restaurant)
            .filter(Restaurant.review_count > 0)
            .order_by(Restaurant.rating.desc(), Restaurant.review_count.desc())
            .limit(25)
            .all()
        )

        # Serialize each restaurant with predicted busyness
        serialized_restaurants = []
        for restaurant in top_restaurants:
            predicted_level = None
            predicted_time = None

            # Fetch the closest busyness prediction for this restaurant's grid_id
            if restaurant.grid_id:
                row = db.session.execute(
                    text(
                        """
                        SELECT predicted_level, timestamp
                        FROM busyness_predictions
                        WHERE grid_id = :gid
                        ORDER BY ABS(EXTRACT(EPOCH FROM timestamp) - :req_epoch)
                        LIMIT 1
                    """
                    ),
                    {"gid": restaurant.grid_id, "req_epoch": req_epoch},
                ).fetchone()

                # Populate prediction details if available
                if row:
                    predicted_level = row.predicted_level
                    predicted_time = row.timestamp

            # Append restaurant details to the list
            serialized_restaurants.append(
                {
                    "restaurant_id": str(restaurant.restaurant_id),
                    "place_id": restaurant.place_id,
                    "full_name": restaurant.full_name,
                    "inspection_id": restaurant.inspection_id,
                    "image_url": restaurant.image_url,
                    "lat": restaurant.lat,
                    "lon": restaurant.lon,
                    "phone": restaurant.phone,
                    "rating": restaurant.rating,
                    "review_count": restaurant.review_count,
                    "address": restaurant.address,
                    "cuisine_type": restaurant.cuisine_type,
                    "cuisine_keyword": restaurant.cuisine_keyword,
                    "inspection_grade": restaurant.inspection_grade,
                    "google_name": restaurant.google_name,
                    "restaurant_counts": restaurant.restaurant_counts,
                    "geometry": (
                        str(restaurant.geometry) if restaurant.geometry else None
                    ),
                    "price_level": restaurant.price_level,
                    "lat_rounded": restaurant.lat_rounded,
                    "lon_rounded": restaurant.lon_rounded,
                    "grid_id": restaurant.grid_id,
                    "wheelchair_friendly": restaurant.wheelchair_friendly,
                    "amenities": restaurant.amenities,
                    "predicted_level": predicted_level,
                    "predicted_time": (
                        predicted_time.isoformat() if predicted_time else None
                    ),
                    "opening_hours": restaurant.opening_hours,
                }
            )

        # Return top 25 restaurant details
        return (
            jsonify(
                {
                    "status": "success",
                    "count": len(serialized_restaurants),
                    "restaurants": serialized_restaurants,
                }
            ),
            200,
        )

    except Exception as e:
        # Return error response
        return jsonify({"status": "error", "message": str(e)}), 500


@main.route("/healthcheck", methods=["GET"])
def healthcheck():
    """
    Basic health check endpoint.

    Description:
        - This endpoint serves as a simple check to confirm that the
          Restaurant Busyness Predictor backend is running and reachable.

    Request (GET):
        No parameters.

    Response (JSON):
        {
            "status": "ok"
        }
    """
    # Return a simple JSON message indicating the backend is operational
    return jsonify({"status": "ok"}), 200
