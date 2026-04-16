import uuid

from app.models import User
from app.utils.authentication_utils import verify_or_create_google_user
from flask import Blueprint, jsonify, request
from flask_jwt_extended import (create_access_token, get_jwt_identity,
                                jwt_required)
from google.auth.transport import requests as grequests
from google.oauth2 import id_token
from werkzeug.security import check_password_hash, generate_password_hash

from app import db

authentication = Blueprint("authentication", __name__)


# Signup endpoint
@authentication.route("/authentication/signup", methods=["POST"])
def signup():
    """
    User signup endpoint
    Expects JSON with: username, email, password, full_name
    Returns: JSON with success message or error
    """
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ["username", "email", "password", "name"]
        for field in required_fields:
            if not data or field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        username = data["username"]
        email = data["email"]
        password = data["password"]
        name = data["name"]
        latitude = data["latitude"]
        longitude = data["longitude"]

        # Check if user already exists
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            return jsonify({"error": "Username or email already exists"}), 409

        # Hash the password
        password_hash = generate_password_hash(password)

        # Create new user
        new_user = User(
            user_id=uuid.uuid4(),
            username=username,
            email=email,
            password_hash=password_hash,
            name=name,
            latitude=latitude,
            longitude=longitude,
        )

        db.session.add(new_user)
        db.session.commit()

        return (
            jsonify(
                {
                    "message": "User created successfully",
                    "user_id": str(new_user.user_id),
                    "username": new_user.username,
                    "email": new_user.email,
                    "name": new_user.name,
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# Login endpoint
@authentication.route("/authentication/login", methods=["POST"])
def login():
    """
    User login endpoint
    Expects JSON with: username, password
    Returns: JSON with JWT token or error
    """
    try:
        data = request.get_json()

        # Validate required fields by usernamer and password
        if not data or "username" not in data or "password" not in data:
            return jsonify({"error": "Missing username or password"}), 400

        username = data["username"]
        password = data["password"]

        # Find user by username
        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({"error": "Invalid username or password"}), 401

        # Create JWT token
        access_token = create_access_token(identity=str(user.user_id))

        return (
            jsonify(
                {
                    "message": "Login successful",
                    "access_token": access_token,
                    "user": {
                        "user_id": str(user.user_id),
                        "username": user.username,
                        "email": user.email,
                        "name": user.name,
                        "location": {
                            "latitude": user.latitude,
                            "longitude": user.longitude,
                        },
                    },
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500


@authentication.route("/authentication/google", methods=["POST"])
def google_login():
    try:
        data = request.get_json()
        token = data.get("credential")
        location = data.get("location")

        if not token:
            return jsonify({"error": "Missing Google credential"}), 400

        idinfo = id_token.verify_oauth2_token(
            token,
            grequests.Request(),
            "825269171399-nr6gltep04clm8b1saspkf8g0hp1v5kd.apps.googleusercontent.com",
            clock_skew_in_seconds=240,
        )

        user, token = verify_or_create_google_user(idinfo, location)

        return (
            jsonify(
                {
                    "message": "Google login successful",
                    "access_token": token,
                    "user": {
                        "user_id": str(user.user_id),
                        "username": user.username,
                        "email": user.email,
                        "name": user.name,
                        "location": {
                            "latitude": user.latitude,
                            "longitude": user.longitude,
                        },
                    },
                }
            ),
            200,
        )

    except PermissionError as e:
        return jsonify({"error": str(e)}), 409

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# Get profile endpoint(optional)
# This endpoint retrieves the user's profile information.
@authentication.route("/authentication/profile", methods=["GET", "OPTIONS"])
@jwt_required()  # using jwt token to verify user is logged in
def get_profile():
    """
    Get user profile endpoint
    Requires: Valid JWT token in Authorization header
    Returns: JSON with user profile data
    """

    if request.method == "OPTIONS":
        return "", 204

    try:
        # Get user ID from JWT token
        current_user_id = get_jwt_identity()

        # Find user by ID
        user = User.query.filter_by(user_id=current_user_id).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        return (
            jsonify(
                {
                    "user_id": str(user.user_id),
                    "username": user.username,
                    "email": user.email,
                    "name": user.name,
                    "latitude": user.latitude,
                    "longitude": user.longitude,
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500


# Update profile endpoint
@authentication.route("/authentication/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    """
    Update user profile endpoint
    Requires: Valid JWT token in Authorization header
    Expects: JSON with fields to update (name, latitude, longitude)
    Returns: JSON with updated user data
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        user = User.query.filter_by(user_id=current_user_id).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Update allowed fields
        if "name" in data:
            user.name = data["name"]
        if "latitude" in data:
            user.latitude = data["latitude"]
        if "longitude" in data:
            user.longitude = data["longitude"]

        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Profile updated successfully",
                    "user_id": str(user.user_id),
                    "username": user.username,
                    "email": user.email,
                    "name": user.name,
                    "latitude": user.latitude,
                    "longitude": user.longitude,
                }
            ),
            200,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500
