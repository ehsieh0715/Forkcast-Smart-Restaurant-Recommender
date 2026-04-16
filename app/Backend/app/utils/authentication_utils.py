import uuid

from app.models import User
from flask_jwt_extended import create_access_token

from app import db


def verify_or_create_google_user(idinfo, location):
    """
    Safely verifies or creates a user from a verified Google token payload.
    Returns (user, access_token) or raises appropriate exceptions.
    """
    email = idinfo.get("email")
    name = idinfo.get("name", "")
    given_name = idinfo.get("given_name", "")
    base_username = given_name or email.split("@")[0]

    latitude = longitude = None
    if location:
        latitude = location.get("latitude")
        longitude = location.get("longitude")

    if not email:
        raise ValueError("Email is required from Google token")

    # Check if user already exists by email
    user = User.query.filter_by(email=email).first()

    if user:
        # Local (form-based) account already exists → block login
        if user.password_hash:
            raise PermissionError("Email already registered using password login")
        # Returning Google user → login allowed
    else:
        # Make sure username is unique
        username = base_username
        suffix = 1
        while User.query.filter_by(username=username).first():
            username = f"{base_username}{suffix}"
            suffix += 1

        # Create new user with optional location
        user = User(
            user_id=uuid.uuid4(),
            username=username,
            email=email,
            name=name,
            password_hash=None,
        )

        if latitude is not None and longitude is not None:
            user.latitude = latitude
            user.longitude = longitude

        db.session.add(user)
        db.session.commit()

    # Issue JWT
    access_token = create_access_token(identity=str(user.user_id))
    return user, access_token
