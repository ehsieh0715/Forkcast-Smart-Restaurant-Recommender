import traceback
import uuid
from datetime import datetime

import pytz
from app.models import *
from app.utils.comparison_utils import *
from app.utils.main_utils import *
from dateutil.parser import isoparse
from flask import Blueprint, jsonify, request
from sqlalchemy import func

from app import db

# Blueprint for comparison-related routes
comparison = Blueprint("comparison", __name__)
# Timezone for New York
ny_tz = pytz.timezone("America/New_York")


# ----------------------------------------------------------------------
# Create a Comparison Session
# ----------------------------------------------------------------------
@comparison.route("/comparison/session/create", methods=["POST"])
def create_comparison_session():
    """
    Create or retrieve a comparison session for a given user.

    Description:
        - This endpoint either creates a new comparison session for the provided user_id,
          or returns an existing active session if one already exists for that user.
        - A comparison session allows users to add/remove restaurants and view them later.

    Request (JSON, POST):
        {
            "user_id": "<UUID string of an existing user>"
        }

    Response (JSON):
        {
            "status": "success",
            "created_by": "<UUID string of the user>",
            "created_at": "<ISO 8601 datetime string of session creation>",
            "session_id": "<UUID string of the session>"
        }
    """
    try:
        # Parse and validate user_id from request body
        data = request.get_json()
        user_id = data.get("user_id")
        # Validate user_id format
        if not user_id:
            return (
                jsonify({"status": "error", "message": "Missing user_id"}),
                400,
            )  # Return error if user_id is missing
        user = (
            db.session.query(User).filter_by(user_id=uuid.UUID(user_id)).first()
        )  # Validate user exists
        if not user:
            return (
                jsonify({"status": "error", "message": "User not found"}),
                404,
            )  # Return error if user not found
        existing_session = (
            db.session.query(ComparisonSession)
            .filter_by(created_by=user.user_id)
            .first()
        )  # Check if user already has a session
        if existing_session:  # If session exists, return it
            return (
                jsonify(
                    {  # Return existing session details
                        "status": "success",
                        "created_by": str(existing_session.created_by),
                        "created_at": existing_session.created_at.isoformat(),
                        "session_id": str(existing_session.session_id),
                    }
                ),
                200,
            )
        now = datetime.now(ny_tz)  # Create new session
        new_session = ComparisonSession(  # Create new session with user_id
            created_by=user.user_id,
            created_at=now,
            restaurants_json=[],  # Initialize with empty restaurant list
        )
        db.session.add(new_session)  # Add new session to database
        db.session.commit()  # Commit changes to database
        return (
            jsonify(
                {
                    "status": "success",
                    "created_by": str(new_session.created_by),
                    "created_at": new_session.created_at.isoformat(),
                    "session_id": str(new_session.session_id),
                }
            ),
            201,
        )
    except Exception as e:  # Handle any exceptions
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


# ----------------------------------------------------------------------
# Add a Restaurant to an Existing Comparison Session
# ----------------------------------------------------------------------
@comparison.route("/comparison/session/<session_id>/add_restaurant", methods=["POST"])
def add_restaurant_to_comparison(session_id):
    """
    Add a restaurant to an existing comparison session.

    Description:
        - This endpoint allows the owner of a comparison session to add a new restaurant
          to the session's restaurant list.
        - It verifies that the session exists and that the requesting user is the owner.
        - If the restaurant is already in the list, it will not be duplicated.

    Request (JSON, POST):
        {
            "user_id": "<UUID string of the session owner>",
            "restaurant_id": "<UUID string of the restaurant to add>"
        }

    Response (JSON):
        {
            "status": "success",
            "message": "Restaurant added to session."
        }
    """
    try:
        # Convert the provided session_id to a UUID
        session_uuid = uuid.UUID(session_id)

        # Retrieve the comparison session from the database
        session = (
            db.session.query(ComparisonSession)
            .filter_by(session_id=session_uuid)
            .first()
        )

        # If no session exists with this ID, return an error
        if not session:
            return jsonify({"status": "error", "message": "Session not found"}), 404

        # Parse the JSON body for user_id and restaurant_id
        data = request.get_json()
        user_id = data.get("user_id")
        restaurant_id = data.get("restaurant_id")

        # Validate that both required fields are present
        if not user_id or not restaurant_id:
            return (
                jsonify(
                    {"status": "error", "message": "Missing user_id or restaurant_id"}
                ),
                400,
            )

        # Validate that the user is the creator of this session
        user_uuid = uuid.UUID(user_id)
        if session.created_by != user_uuid:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Unauthorized: You do not own this session.",
                    }
                ),
                403,
            )

        # Initialize restaurants_json if it is currently None
        if session.restaurants_json is None:
            session.restaurants_json = []

        # Add restaurant only if not already present
        if restaurant_id not in session.restaurants_json:
            session.restaurants_json.append(
                restaurant_id
            )  # Append the new restaurant ID
            db.session.commit()  # Commit the updated session back to the database

        # Return a success message
        return (
            jsonify({"status": "success", "message": "Restaurant added to session."}),
            200,
        )

    except Exception as e:
        # Print full traceback for debugging and return an error response
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


# ----------------------------------------------------------------------
# Remove a Restaurant from an Existing Comparison Session
# ----------------------------------------------------------------------
@comparison.route(
    "/comparison/session/<session_id>/remove_restaurant", methods=["POST"]
)
def remove_restaurant_from_comparison(session_id):
    """
    Remove a restaurant from an existing comparison session.

    Description:
        - This endpoint allows the owner of a comparison session to remove a restaurant
          from the session's restaurant list.
        - It verifies that the session exists and that the requesting user is the owner.
        - If the restaurant is not currently in the list, no change is made.

    Request (JSON, POST):
        {
            "user_id": "<UUID string of the session owner>",
            "restaurant_id": "<UUID string of the restaurant to remove>"
        }

    Response (JSON):
        {
            "status": "success",
            "message": "Restaurant removed from session."
        }
    """
    try:
        # Convert the provided session_id to a UUID
        session_uuid = uuid.UUID(session_id)

        # Retrieve the comparison session from the database
        session = (
            db.session.query(ComparisonSession)
            .filter_by(session_id=session_uuid)
            .first()
        )

        # If no session exists with this ID, return an error
        if not session:
            return jsonify({"status": "error", "message": "Session not found"}), 404

        # Parse the JSON body for user_id and restaurant_id
        data = request.get_json()
        user_id = data.get("user_id")
        restaurant_id = data.get("restaurant_id")

        # Validate that both required fields are present
        if not user_id or not restaurant_id:
            return (
                jsonify(
                    {"status": "error", "message": "Missing user_id or restaurant_id"}
                ),
                400,
            )

        # Validate that the user is the creator of this session
        user_uuid = uuid.UUID(user_id)
        if session.created_by != user_uuid:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Unauthorized: You do not own this session.",
                    }
                ),
                403,
            )

        # Remove the restaurant if it exists in the list
        if restaurant_id in session.restaurants_json:
            session.restaurants_json.remove(
                restaurant_id
            )  # Remove restaurant from the list
            db.session.commit()  # Commit the updated session back to the database

        # Return a success message
        return (
            jsonify(
                {"status": "success", "message": "Restaurant removed from session."}
            ),
            200,
        )

    except Exception as e:
        # Print full traceback for debugging and return an error response
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


# ----------------------------------------------------------------------
# View an Existing Comparison Session
# ----------------------------------------------------------------------
@comparison.route("/comparison/session/<session_id>/view", methods=["POST"])
def view_comparison_session(session_id):
    """
    View the details of an existing comparison session.

    Description:
        - This endpoint allows the owner of a comparison session to view all restaurants
          currently added to that session.
        - Optionally accepts a requested_time query parameter to fetch busyness predictions
          closest to that time.

    Request (JSON, POST):
        {
            "user_id": "<UUID string of the session owner>"
        }

    Optional Query Parameters:
        requested_time=<ISO 8601 datetime string>
        (If not provided, current time is used.)

    Response (JSON):
        {
            "status": "success",
            "session_id": "<UUID string of the session>",
            "restaurants": [
                {
                    "restaurant_id": "<UUID>",
                    "place_id": "<string>",
                    "full_name": "<string>",
                    "address": "<string>",
                    "rating": <float or null>,
                    "price_level": <int or null>,
                    "review_count": <int or null>,
                    "cuisine_type": "<string>",
                    "cuisine_keyword": "<string>",
                    "inspection_grade": "<string or null>",
                    "lat": <float>,
                    "lon": <float>,
                    "phone": "<string or null>",
                    "image_url": "<string or null>",
                    "google_name": "<string or null>",
                    "predicted_level": <int or null>,
                    "prediction_timestamp": "<ISO 8601 datetime or null>"
                },
                ...
            ]
        }
    """
    try:
        # Convert the provided session_id to a UUID
        session_uuid = uuid.UUID(session_id)

        # Retrieve the comparison session from the database
        session = (
            db.session.query(ComparisonSession)
            .filter_by(session_id=session_uuid)
            .first()
        )

        # If no session exists with this ID, return an error
        if not session:
            return jsonify({"status": "error", "message": "Session not found"}), 404

        # Parse the JSON body for user_id
        data = request.get_json()
        user_id = data.get("user_id")

        # Validate that user_id is present
        if not user_id:
            return jsonify({"status": "error", "message": "Missing user_id"}), 400

        # Validate that the user is the creator of this session
        user_uuid = uuid.UUID(user_id)
        if session.created_by != user_uuid:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Unauthorized: You do not own this session.",
                    }
                ),
                403,
            )

        # Handle optional requested_time query parameter
        requested_time_str = request.args.get("requested_time")
        if requested_time_str:
            try:
                requested_time = isoparse(requested_time_str)  # Parse provided time
            except Exception:
                return (
                    jsonify(
                        {"status": "error", "message": "Invalid requested_time format"}
                    ),
                    400,
                )
        else:
            requested_time = datetime.now(ny_tz)  # Default to current time

        # Convert requested time to epoch seconds for comparison
        req_epoch = requested_time.timestamp()

        # Prepare list of restaurant details
        restaurants = []

        # Loop through restaurant IDs stored in session
        for restaurant_id in session.restaurants_json:
            try:
                restaurant_uuid = uuid.UUID(restaurant_id)  # Validate UUID
            except ValueError:
                continue  # Skip invalid IDs

            # Retrieve restaurant from database
            r = (
                db.session.query(Restaurant)
                .filter_by(restaurant_id=restaurant_uuid)
                .first()
            )
            if not r:
                continue  # Skip if restaurant record not found

            # Retrieve the busyness prediction closest to the requested time
            prediction = (
                db.session.query(BusynessPrediction)
                .filter(BusynessPrediction.grid_id == r.grid_id)
                .order_by(
                    func.abs(
                        func.extract("epoch", BusynessPrediction.timestamp) - req_epoch
                    )
                )
                .first()
            )

            # Append restaurant details to the list
            restaurants.append(
                {
                    "restaurant_id": str(r.restaurant_id),
                    "place_id": r.place_id,
                    "full_name": r.full_name,
                    "address": r.address,
                    "rating": r.rating,
                    "price_level": r.price_level,
                    "review_count": r.review_count,
                    "cuisine_type": r.cuisine_type,
                    "cuisine_keyword": r.cuisine_keyword,
                    "inspection_grade": r.inspection_grade,
                    "lat": r.lat,
                    "lon": r.lon,
                    "phone": r.phone,
                    "image_url": r.image_url,
                    "google_name": r.google_name,
                    "predicted_level": (
                        prediction.predicted_level if prediction else None
                    ),
                    "prediction_timestamp": (
                        prediction.timestamp.isoformat()
                        if prediction and prediction.timestamp
                        else None
                    ),
                }
            )

        # Return the session details with all restaurant data
        return (
            jsonify(
                {
                    "status": "success",
                    "session_id": str(session.session_id),
                    "restaurants": restaurants,
                }
            ),
            200,
        )

    except Exception as e:
        # Print full traceback for debugging and return an error response
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


# ----------------------------------------------------------------------
# Get All Comparison Sessions for a User
# ----------------------------------------------------------------------
@comparison.route("/comparison/user/<user_id>/sessions", methods=["GET"])
def get_user_comparison_sessions(user_id):
    """
    Retrieve all comparison sessions created by a specific user.

    Description:
        - This endpoint returns a list of all comparison sessions that were created
          by the provided user_id.
        - Sessions are sorted by creation date in descending order.
        - Each session includes its ID, creation timestamp, and the number of restaurants stored.

    Request (GET):
        URL parameter:
            user_id = <UUID string of the user>

    Response (JSON):
        {
            "status": "success",
            "sessions": [
                {
                    "session_id": "<UUID string of session>",
                    "created_at": "<ISO 8601 datetime string>",
                    "restaurant_count": <integer>
                },
                ...
            ]
        }
    """
    try:
        # Convert the provided user_id to a UUID
        user_uuid = uuid.UUID(user_id)

        # Query all sessions created by this user, ordered by most recent
        sessions = (
            db.session.query(ComparisonSession)
            .filter_by(created_by=user_uuid)
            .order_by(ComparisonSession.created_at.desc())
            .all()
        )

        # Build a list of session details
        session_list = []
        for s in sessions:
            session_list.append(
                {
                    "session_id": str(
                        s.session_id
                    ),  # Unique identifier for the session
                    "created_at": s.created_at.isoformat(
                        timespec="seconds"
                    ),  # Creation timestamp
                    "restaurant_count": len(
                        s.restaurants_json or []
                    ),  # Number of restaurants in this session
                }
            )

        # Return all sessions for this user
        return jsonify({"status": "success", "sessions": session_list}), 200

    except Exception as e:
        # Print full traceback for debugging and return an error response
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500
