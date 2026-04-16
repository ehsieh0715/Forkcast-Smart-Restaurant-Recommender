import traceback
import uuid
from datetime import datetime

import pytz
from app.models import BusynessPrediction, Group, Restaurant, User
from app.utils.group_utils import calculate_group_fit_score
from app.utils.main_utils import *
from dateutil.parser import isoparse
from flask import Blueprint, jsonify, request
from sqlalchemy import func

from app import db

# Blueprint for group-related routes
group = Blueprint("group", __name__)
# Timezone for New York
ny_tz = pytz.timezone("America/New_York")


# ----------------------------------------------------------------------
# Create a New Group Session
# ----------------------------------------------------------------------
@group.route("/group/session/create", methods=["POST"])
def create_group_session():
    """
    Create a new group session.

    Description:
        - This endpoint creates a new group session with a specified group name and creator.
        - It validates that the group name is unique and that the creator exists.
        - On creation, the creator is automatically added to the members list.

    Request (JSON, POST):
        {
            "group_name": "<string name of the group>",
            "created_by": "<UUID string of the user creating the group>"
        }

    Response (JSON):
        {
            "status": "success",
            "group_id": "<UUID string of the new group>",
            "group_name": "<string name of the group>",
            "members_json": {
                "<creator_uuid>": {
                    "user_name": "<creator's name>"
                }
            }
        }
    """
    try:
        # Parse the JSON body for required fields
        data = request.get_json()
        group_name = data.get("group_name")
        created_by = data.get("created_by")

        # Validate both group_name and created_by are provided
        if not group_name or not created_by:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Both group_name and created_by are required.",
                    }
                ),
                400,
            )

        # Check if a group with the same name already exists
        if db.session.query(Group).filter_by(group_name=group_name).first():
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Group with that name already exists",
                    }
                ),
                400,
            )

        # Validate that the creator exists in the User table
        creator_uuid = uuid.UUID(created_by)
        user_obj = db.session.query(User).filter_by(user_id=creator_uuid).first()
        if not user_obj:
            return jsonify({"status": "error", "message": "Creator not found"}), 400

        # Initialize members_json with the creator
        members_json = {str(created_by): {"user_name": user_obj.name}}

        # Create the new Group object
        new_group = Group(
            group_name=group_name, created_by=created_by, members_json=members_json
        )

        # Add and commit the new group to the database
        db.session.add(new_group)
        db.session.commit()

        # Return the group details
        return (
            jsonify(
                {
                    "status": "success",
                    "group_id": str(new_group.group_id),
                    "group_name": group_name,
                    "members_json": members_json,
                }
            ),
            201,
        )

    except Exception as e:
        # Print full traceback, rollback the transaction, and return error response
        traceback.print_exc()
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500


# ----------------------------------------------------------------------
# Delete an Existing Group Session
# ----------------------------------------------------------------------
@group.route("/group/session/<group_id>", methods=["DELETE"])
def delete_group_session(group_id):
    """
    Delete an existing group session.

    Description:
        - This endpoint deletes a group session identified by its group_id.
        - Once deleted, all associated data for the group session is removed from the database.

    Request (DELETE):
        URL parameter:
            group_id = <UUID string of the group to delete>

    Response (JSON):
        {
            "status": "success",
            "message": "Group deleted"
        }
    """
    try:
        # Convert the provided group_id to a UUID
        gid = uuid.UUID(group_id)

        # Retrieve the group session from the database
        group_obj = db.session.query(Group).filter_by(group_id=gid).first()

        # If the group session does not exist, return an error
        if not group_obj:
            return jsonify({"status": "error", "message": "Group not found"}), 404

        # Delete the group session and commit the change
        db.session.delete(group_obj)
        db.session.commit()

        # Return a success message
        return jsonify({"status": "success", "message": "Group deleted"}), 200

    except Exception as e:
        # Print full traceback for debugging and return an error response
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


# ----------------------------------------------------------------------
# Submit Preferences for a Group Session
# ----------------------------------------------------------------------
@group.route("/group/session/<group_id>/submit_preferences", methods=["POST"])
def submit_preferences(group_id):
    """
    Submit preferences for a specific group session.

    Description:
        - This endpoint allows a user to submit their restaurant preferences
          to an existing group session.
        - If a user_id is not provided, a guest user_id is generated automatically.
        - Preferences are stored in the group's members_json, keyed by user_id.

    Request (JSON, POST):
        {
            "user_id": "<UUID string of the user> (optional, guest ID will be created if not provided)",
            "preferences": {
                "cuisine_type": "<string>",
                "price_level": <1 | 2 | 3>,
                "other_preference_key": "<value>"
            }
        }

    Response (JSON):
        {
            "status": "success",
            "user_id": "<UUID string or generated guest ID>"
        }
    """
    try:
        # Parse the JSON body for user_id and preferences
        data = request.get_json()
        user_id = data.get(
            "user_id", f"guest-{uuid.uuid4()}"
        )  # Use provided ID or generate guest ID
        preferences = data.get("preferences")

        # Validate that preferences is a dictionary
        if not isinstance(preferences, dict):
            return (
                jsonify(
                    {"status": "error", "message": "preferences must be an object"}
                ),
                400,
            )

        # Validate price_level if provided
        if "price_level" in preferences and preferences["price_level"] not in [1, 2, 3]:
            return (
                jsonify(
                    {"status": "error", "message": "price_level must be 1, 2, or 3"}
                ),
                400,
            )

        # Convert group_id to UUID and retrieve group from database
        gid = uuid.UUID(group_id)
        group_obj = db.session.query(Group).filter_by(group_id=gid).first()

        # If group is not found, return an error
        if not group_obj:
            return jsonify({"status": "error", "message": "Group not found"}), 404

        # Get current members_json and update with new preferences
        members = dict(group_obj.members_json) if group_obj.members_json else {}

        # If user already exists, preserve their user_name in preferences
        if user_id in members and "user_name" in members[user_id]:
            preferences["user_name"] = members[user_id]["user_name"]

        # Update or add this user's preferences
        members[user_id] = preferences
        group_obj.members_json = members

        # Commit the changes to the database
        db.session.commit()

        # Return a success message with the user_id
        return jsonify({"status": "success", "user_id": user_id}), 200

    except Exception as e:
        # Print full traceback, rollback in case of error, and return error response
        traceback.print_exc()
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500


# ----------------------------------------------------------------------
# Update Preferences for a Group Session
# ----------------------------------------------------------------------
@group.route("/group/session/<group_id>/update_preferences", methods=["PUT"])
def update_preferences(group_id):
    """
    Update existing preferences for a specific group session.

    Description:
        - This endpoint allows a user to update their previously submitted preferences
          within a group session.
        - The user_id must already exist in the group's members_json for this update
          to replace their current preferences.

    Request (JSON, PUT):
        {
            "user_id": "<UUID string of the user>",
            "preferences": {
                "cuisine_type": "<string>",
                "price_level": <1 | 2 | 3>,
                "other_preference_key": "<value>"
            }
        }

    Response (JSON):
        {
            "status": "success"
        }
    """
    try:
        # Parse the JSON body for user_id and new preferences
        data = request.get_json()
        user_id = data.get("user_id")
        new_prefs = data.get("preferences")

        # Validate that both user_id and preferences are provided
        if not user_id or not isinstance(new_prefs, dict):
            return (
                jsonify(
                    {"status": "error", "message": "Missing user_id or preferences"}
                ),
                400,
            )

        # Validate price_level if present
        if "price_level" in new_prefs and new_prefs["price_level"] not in [1, 2, 3]:
            return (
                jsonify(
                    {"status": "error", "message": "price_level must be 1, 2, or 3"}
                ),
                400,
            )

        # Convert group_id to UUID and retrieve group from database
        gid = uuid.UUID(group_id)
        group_obj = db.session.query(Group).filter_by(group_id=gid).first()

        # If group not found, return an error
        if not group_obj:
            return jsonify({"status": "error", "message": "Group not found"}), 404

        # Retrieve the current members_json and update with new preferences
        members = group_obj.members_json or {}
        members[user_id] = new_prefs
        group_obj.members_json = members

        # Commit updated preferences to the database
        db.session.commit()

        # Return a success message
        return jsonify({"status": "success"}), 200

    except Exception as e:
        # Print full traceback for debugging and return an error response
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


# ----------------------------------------------------------------------
# Get Members of a Group Session
# ----------------------------------------------------------------------
@group.route("/group/session/<group_id>/members", methods=["GET"])
def get_group_members(group_id):
    """
    Retrieve the members of a specific group session.

    Description:
        - This endpoint returns all members currently stored in the group's members_json.
        - It also returns the user_id of the creator of the group.

    Request (GET):
        URL parameter:
            group_id = <UUID string of the group>

    Response (JSON):
        {
            "status": "success",
            "group": {
                "members": {
                    "<user_id_1>": { ...preferences and/or user_name... },
                    "<user_id_2>": { ... },
                    ...
                },
                "created_by": "<UUID string of the creator>"
            }
        }
    """
    try:
        # Convert the provided group_id to a UUID
        gid = uuid.UUID(group_id)

        # Retrieve the group object from the database
        group_obj = db.session.query(Group).filter_by(group_id=gid).first()

        # If no group is found with this ID, return an error
        if not group_obj:
            return jsonify({"status": "error", "message": "Group not found"}), 404

        # Return the group's members and creator
        return (
            jsonify(
                {
                    "status": "success",
                    "group": {
                        "members": group_obj.members_json,
                        "created_by": group_obj.created_by,
                    },
                }
            ),
            200,
        )

    except Exception as e:
        # Print full traceback for debugging and return an error response
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


# ----------------------------------------------------------------------
# Clear All Preferences in a Group Session (Except Creator Entry)
# ----------------------------------------------------------------------
@group.route("/group/session/<group_id>/clear", methods=["DELETE"])
def clear_group_preferences(group_id):
    """
    Clear all member preferences from a specific group session.

    Description:
        - This endpoint removes all submitted preferences from the group's members_json,
          while preserving an empty entry for the creator.
        - Useful for resetting a group session without deleting it.

    Request (DELETE):
        URL parameter:
            group_id = <UUID string of the group>

    Response (JSON):
        {
            "status": "success"
        }
    """
    try:
        # Convert the provided group_id to a UUID
        gid = uuid.UUID(group_id)

        # Retrieve the group object from the database
        group_obj = db.session.query(Group).filter_by(group_id=gid).first()

        # If no group is found with this ID, return an error
        if not group_obj:
            return jsonify({"status": "error", "message": "Group not found"}), 404

        # Preserve creator_id with an empty object and clear all others
        creator_id = str(group_obj.created_by)
        group_obj.members_json = {creator_id: {}}  # Reset members_json

        # Commit the changes to the database
        db.session.commit()

        # Return a success message
        return jsonify({"status": "success"}), 200

    except Exception as e:
        # Print full traceback for debugging and return an error response
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


# ----------------------------------------------------------------------
# Get Group Session Recommendations (Results)
# ----------------------------------------------------------------------
@group.route("/group/session/<group_id>/results", methods=["GET"])
def group_session_results(group_id):
    """
    Retrieve restaurant recommendations for a group session (optimized).

    Description:
        - Computes and returns a ranked list of restaurant recommendations
          for a given group session based on all members' preferences.
        - Requires the user's latitude, longitude, and a desired datetime
          to retrieve busyness predictions.
        - Performance improvements:
            • Pre‑filters restaurants within a geographic bounding box around
              the user's location.
            • Bulk‑fetches all relevant busyness predictions in a single query
              instead of querying per restaurant.
            • Selects the nearest prediction timestamp in memory rather than
              running separate database sorts.

    Request (GET):
        Query parameters:
            latitude = <float latitude of user location>
            longitude = <float longitude of user location>
            desired_datetime = <ISO 8601 datetime string>
        URL parameter:
            group_id = <UUID string of the group>

    Response (JSON):
        {
            "status": "success",
            "recommendations": [
                {
                    "restaurant_id": "<UUID>",
                    "full_name": "<string>",
                    "fit_score": <float>,
                    "distance_meters": <int>,
                    "predicted_level": <int>,
                    "predicted_timestamp": "<ISO 8601 datetime or null>",
                    ... other restaurant fields ...
                },
                ...
            ]
        }
    """
    try:
        # ---------------------------
        # 1. Validate input
        # ---------------------------
        lat = request.args.get("latitude")
        lon = request.args.get("longitude")
        desired_datetime_str = request.args.get("desired_datetime")

        if not lat or not lon or not desired_datetime_str:
            return jsonify({"status": "error",
                            "message": "Missing query parameters: latitude, longitude, desired_datetime are required."}), 400

        try:
            user_lat = float(lat)
            user_lon = float(lon)
        except ValueError:
            return jsonify({"status": "error", "message": "Invalid latitude/longitude format"}), 400

        try:
            desired_datetime = isoparse(desired_datetime_str)
        except Exception:
            return jsonify({"status": "error", "message": "Invalid desired_datetime format"}), 400

        # ---------------------------
        # 2. Load group
        # ---------------------------
        gid = uuid.UUID(group_id)
        group_obj = db.session.query(Group).filter_by(group_id=gid).first()
        if not group_obj:
            return jsonify({"status": "error", "message": "Group not found"}), 404

        group_preferences = list((group_obj.members_json or {}).values())

        # Normalize cuisine preferences
        for prefs in group_preferences:
            cp = prefs.get("cuisine_preferences")
            if isinstance(cp, list):
                cuisine_list = []
                for item in cp:
                    if isinstance(item, str):
                        cuisine_list.extend([c.strip() for c in item.split(",") if c.strip()])
                prefs["cuisine_preferences"] = ", ".join(cuisine_list)
            elif isinstance(cp, str):
                prefs["cuisine_preferences"] = ", ".join([c.strip() for c in cp.split(",") if c.strip()])
            elif isinstance(cp, dict):
                prefs["cuisine_preferences"] = ", ".join([k.strip().lower() for k in cp.keys()])
            else:
                prefs["cuisine_preferences"] = ""

        # ---------------------------
        # 3. Pre-filter restaurants by bounding box
        # ---------------------------
        delta = 0.5  # ~55 km; adjust as needed
        lat_min, lat_max = user_lat - delta, user_lat + delta
        lon_min, lon_max = user_lon - delta, user_lon + delta

        restaurants = db.session.query(Restaurant).filter(
            Restaurant.lat.between(lat_min, lat_max),
            Restaurant.lon.between(lon_min, lon_max)
        ).all()

        if not restaurants:
            return jsonify({"status": "success", "recommendations": []}), 200

        # Collect all grid_ids
        grid_ids = [r.grid_id for r in restaurants if r.grid_id]

        # ---------------------------
        # 4. Bulk fetch predictions within a time window
        # ---------------------------
        window_start = desired_datetime - timedelta(hours=2)
        window_end = desired_datetime + timedelta(hours=2)

        prediction_rows = db.session.query(BusynessPrediction).filter(
            BusynessPrediction.grid_id.in_(grid_ids),
            BusynessPrediction.timestamp.between(window_start, window_end)
        ).all()

        # Group predictions by grid_id and pick nearest timestamp
        from collections import defaultdict
        predictions_map = defaultdict(list)
        for p in prediction_rows:
            predictions_map[p.grid_id].append(p)

        nearest_prediction = {}
        for gid_val, plist in predictions_map.items():
            closest = min(plist, key=lambda p: abs((p.timestamp - desired_datetime).total_seconds()))
            nearest_prediction[gid_val] = closest

        # ---------------------------
        # 5. Build recommendations
        # ---------------------------
        recommendations = []
        for r in restaurants:
            p = nearest_prediction.get(r.grid_id)
            if not p:
                continue
            fit_score, distance_meters = calculate_group_fit_score(
                r, p, group_preferences, user_lat, user_lon
            )
            recommendations.append({
                "restaurant_id": str(r.restaurant_id),
                "image_url": r.image_url,
                "place_id": r.place_id,
                "full_name": r.full_name,
                "address": r.address,
                "rating": r.rating,
                "review_count": r.review_count,
                "cuisine_type": r.cuisine_type,
                "price_level": r.price_level,
                "fit_score": round(fit_score, 3),
                "distance_meters": int(distance_meters),
                "predicted_level": p.predicted_level,
                "predicted_timestamp": p.timestamp.isoformat() if p.timestamp else None
            })

        recommendations.sort(key=lambda x: x["fit_score"], reverse=True)
        return jsonify({"status": "success", "recommendations": recommendations[:100]}), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


# ----------------------------------------------------------------------
# Join an Existing Group Session
# ----------------------------------------------------------------------
@group.route("/group/session/<group_id>/join", methods=["POST"])
def join_group_session(group_id):
    """
    Join an existing group session.

    Description:
        - This endpoint allows a user to join a group session by adding their user_id
          and name (if available) to the group's members_json.
        - If the user is already a member, no duplicate entry is created.

    Request (JSON, POST):
        {
            "user_id": "<UUID string of the user joining>"
        }

    Response (JSON):
        {
            "status": "success",
            "group": {
                "group_id": "<UUID string of the group>",
                "group_name": "<string name of the group>",
                "members": {
                    "<user_id_1>": { "user_name": "<name>" },
                    "<user_id_2>": { "user_name": "<name>" },
                    ...
                },
                "created_by": "<UUID string of the creator>"
            }
        }
    """
    try:
        # Parse JSON body to get user_id
        data = request.get_json()
        user_id = data.get("user_id")

        # Validate user_id is provided
        if not user_id:
            return jsonify({"status": "error", "message": "user_id is required"}), 400

        # Convert group_id to UUID and retrieve group object
        gid = uuid.UUID(group_id)
        group_obj = db.session.query(Group).filter_by(group_id=gid).first()

        # Retrieve user object from database
        user = db.session.query(User).filter_by(user_id=user_id).first()

        # If group not found, return an error
        if not group_obj:
            return jsonify({"status": "error", "message": "Group not found"}), 404

        # Prepare members_json and add new member if not already present
        members = dict(group_obj.members_json) if group_obj.members_json else {}
        if user_id not in members:
            members[user_id] = {"user_name": user.name if user else ""}

        # Update members_json and commit changes
        group_obj.members_json = members
        db.session.commit()

        # Return updated group details
        return (
            jsonify(
                {
                    "status": "success",
                    "group": {
                        "group_id": str(group_obj.group_id),
                        "group_name": group_obj.group_name,
                        "members": group_obj.members_json,
                        "created_by": group_obj.created_by,
                    },
                }
            ),
            200,
        )

    except Exception as e:
        # Print full traceback for debugging and return an error response
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


# ----------------------------------------------------------------------
# Get All Groups a User Belongs To
# ----------------------------------------------------------------------
@group.route("/group/user/<user_id>/groups", methods=["GET"])
def get_groups_by_user(user_id):
    """
    Retrieve all groups that a specific user is a member of.

    Description:
        - This endpoint returns a list of all groups where the given user_id
          appears in the group's members_json.

    Request (GET):
        URL parameter:
            user_id = <UUID string of the user>

    Response (JSON):
        {
            "status": "success",
            "groups": [
                {
                    "group_id": "<UUID string of the group>",
                    "group_name": "<string name of the group>"
                },
                ...
            ]
        }
    """
    try:
        # Query all groups from the database
        all_groups = db.session.query(Group).all()

        # Build a list of groups where the user_id is found in members_json
        user_groups = []
        for g in all_groups:
            members = g.members_json or {}
            if user_id in members:
                user_groups.append(
                    {
                        "group_id": str(g.group_id),  # Unique identifier for the group
                        "group_name": g.group_name,  # Name of the group
                    }
                )

        # Return the list of groups the user belongs to
        return jsonify({"status": "success", "groups": user_groups}), 200

    except Exception as e:
        # Print full traceback for debugging and return an error response
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500
