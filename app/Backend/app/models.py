# Models for the Flask application using SQLAlchemy

# Import necessary libraries and modules
import os  # OS module to interact with environment variables
import uuid  # For generating UUID primary keys
from datetime import datetime, timezone  # For working with timestamp fields

from dotenv import load_dotenv  # Load environment variables from .env file
from flask_sqlalchemy import SQLAlchemy  # SQLAlchemy ORM for database models
from geoalchemy2 import Geometry  # For spatial data types (PostGIS)
from sqlalchemy import Date  # SQLAlchemy core types
from sqlalchemy import (Boolean, Column, DateTime, Float, ForeignKey, Integer,
                        String, func)
from sqlalchemy.dialects.postgresql import (  # PostgreSQL-specific column types
    ARRAY, DATE, INTERVAL, JSON, JSONB, TEXT, TIMESTAMP, UUID)
from sqlalchemy.ext.mutable import (  # Makes JSONB arrays mutable in SQLAlchemy; Makes JSONB objects mutable in SQLAlchemy
    MutableDict, MutableList)
from sqlalchemy.schema import \
    UniqueConstraint  # Used to enforce unique constraints on specific columns

from app import db  # Import db object from app package (SQLAlchemy instance)

load_dotenv()  # Load environment variables from .env file into environment


# Define the User model
class User(db.Model):
    __tablename__ = "users"

    user_id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )  # Primary key, UUID format
    name = Column(String(80), nullable=False)  # User's full name (required field)
    username = Column(
        String(80), unique=True, nullable=False
    )  # Username (must be unique and not null)
    email = Column(
        String(120), unique=True, nullable=False
    )  # Email (must be unique and not null)
    password_hash = db.Column(
        db.String(255), nullable=True
    )  # Optional hashed password for login
    latitude = Column(Float, nullable=True)  # Optional latitude field for user location
    longitude = Column(
        Float, nullable=True
    )  # Optional longitude field for user location

    def __repr__(self):
        return (
            f"<{self.name}, is {self.username}>"  # String representation for debugging
        )


# Define the Restaurant model
class Restaurant(db.Model):
    __tablename__ = "restaurants"

    restaurant_id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )  # Primary key UUID
    place_id = Column(String)  # External Place ID (e.g., from Google Maps)
    full_name = Column(
        String, unique=True
    )  # Full name of the restaurant (must be unique)
    inspection_id = Column(String)  # Unique inspection ID from NYC DOHMH
    image_url = Column(String)  # Optional image URL for visual reference
    lat = Column(Float, nullable=False)  # Latitude coordinate
    lon = Column(Float, nullable=False)  # Longitude coordinate
    phone = Column(String)  # Contact phone number
    rating = Column(Float)  # Average rating (e.g., 4.5 stars)
    review_count = Column(Integer)  # Total number of reviews
    address = Column(String)  # Full street address
    inspection_date = Column(Date)  # Most recent health inspection date
    cuisine_type = Column(String)  # Main cuisine type (e.g., Italian)
    cuisine_keyword = Column(
        JSON
    )  # JSON list of cuisine keywords (e.g., [{alias:..., title:...}])
    inspection_grade = Column(String)  # Letter grade (A/B/C) from health dept
    google_name = Column(String, nullable=True)  # Name as listed on Google
    restaurant_counts = Column(
        Integer, nullable=True
    )  # Count of restaurants in the same grid (optional)
    geometry = Column(
        Geometry("POINT"), nullable=True
    )  # Geospatial point location (PostGIS)
    price_level = Column(
        Integer, nullable=True
    )  # Price category: 1=cheap, 2=medium, 3=expensive
    lat_rounded = Column(Float, nullable=True)  # Rounded latitude for grid bucketing
    lon_rounded = Column(Float, nullable=True)  # Rounded longitude for grid bucketing
    grid_id = Column(
        String,
        ForeignKey("busyness_predictions.grid_id", ondelete="SET NULL"),
        nullable=True,
    )  # Grid zone ID
    has_opening_hour_data = Column(
        Boolean, nullable=True
    )  # Whether we have opening hour info
    distance_to_fairfax = Column(
        Float, nullable=True
    )  # Precomputed distance to Fairfax (used for benchmarking)
    distance_to_stella_34_trattoria = Column(
        Float, nullable=True
    )  # Precomputed distance to Stella Trattoria
    distance_to_old_homestead_steakhouse = Column(
        Float, nullable=True
    )  # Precomputed distance to Old Homestead
    wheelchair_friendly = Column(
        Boolean, nullable=True
    )  # Whether the restaurant is wheelchair accessible (True/False)
    opening_hours = Column(
        JSON, nullable=True
    )  # JSON object of daily opening hours (e.g., {"Monday": ["09:00–17:00"]})
    amenities = Column(
        JSON, nullable=True
    )  # JSON list of amenities (e.g., ["WiFi", "Outdoor seating"])

    def __repr__(self):
        return f"<Restaurant {self.full_name}>"  # String representation for debugging


# Define the Group model
class Group(db.Model):
    __tablename__ = "groups"

    group_id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )  # Unique identifier for the group
    group_name = Column(String, nullable=True)  # Optional group display name
    created_by = Column(
        UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False
    )  # Creator's user_id
    created_at = Column(
        DateTime(timezone=True), server_default=func.now()
    )  # Creation timestamp
    members_json = Column(
        MutableDict.as_mutable(JSONB), nullable=False
    )  # JSONB object with user_id: preferences mapping

    def __repr__(self):
        return f"<Group {self.group_name or self.group_id}>"  # Human-readable display


# Define the BusynessPrediction table
class BusynessPrediction(db.Model):
    __tablename__ = "busyness_predictions"
    __table_args__ = (
        UniqueConstraint("grid_id", name="uq_grid_id"),
    )  # Enforce uniqueness on grid_id

    grid_id = Column(
        String, primary_key=True, nullable=False
    )  # Grid location identifier
    timestamp = Column(
        DateTime(timezone=True), primary_key=True, nullable=False
    )  # Timestamp of the prediction
    predicted_level = Column(
        Integer, nullable=False
    )  # Busyness level on a scale of 1–5

    def __repr__(self):
        return f"<BusynessPrediction grid={self.grid_id} @ {self.timestamp} = {self.predicted_level}>"


# Group Fit Score table
class GroupFitScore(db.Model):
    __tablename__ = "group_fit_scores"

    score_id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )  # Unique fit score ID
    group_id = Column(
        UUID(as_uuid=True), ForeignKey("groups.group_id"), nullable=False
    )  # Reference to group
    restaurant_id = Column(
        UUID(as_uuid=True), ForeignKey("restaurants.restaurant_id"), nullable=False
    )  # Restaurant rated
    timestamp = Column(
        DateTime(timezone=True), server_default=func.now()
    )  # Timestamp of scoring
    fit_score = Column(Float, nullable=False)  # Score between 0 and 1
    fit_breakdown = Column(JSONB, nullable=True)  # Optional detailed scoring breakdown

    def __repr__(self):
        return f"<FitScore {self.fit_score} for Group {self.group_id}>"


# Personal Fit Score table
class PersonalFitScore(db.Model):
    __tablename__ = "personal_fit_scores"

    score_id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )  # Unique fit score ID
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.user_id")
    )  # User being scored for
    restaurant_id = Column(
        UUID(as_uuid=True), ForeignKey("restaurants.restaurant_id")
    )  # Restaurant evaluated
    timestamp = Column(
        DateTime, default=datetime.now(timezone.utc)
    )  # Timestamp of score computation
    fit_score = Column(Float)  # Score between 0 and 1
    fits_breakdown = Column(JSON)  # Optional feature-wise breakdown


# Session-based Comparison table (short-lived user sessions)
class ComparisonSession(db.Model):
    __tablename__ = "comparison_sessions"

    session_id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )  # Unique session ID
    created_by = Column(
        UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False
    )  # Creator's user_id
    created_at = Column(
        DateTime(timezone=True), default=datetime.now(timezone.utc)
    )  # Creation time
    restaurants_json = Column(
        MutableList.as_mutable(JSONB), nullable=False, default=list
    )  # List of restaurant UUIDs

    def __repr__(self):
        return f"<ComparisonSession {self.session_id}>"


# LocationMapping model used for named geospatial overlays
class LocationMapping(db.Model):
    __tablename__ = "location_mapping"
    main_location = Column(String, primary_key=True)  # Label/key for the region
    geometry = Column(Geometry("POLYGON"))  # PostGIS polygon geometry


# Grid metadata
class GridInfo(db.Model):
    __tablename__ = "grid_info"
    grid_id = Column(String, primary_key=True)  # Grid ID
    lat = Column(Float)  # Center latitude
    lon = Column(Float)  # Center longitude
    geometry = Column(Geometry("POLYGON"))  # Polygon shape of the grid cell
    restaurant_count = Column(Integer)  # Number of restaurants inside
    population = Column(Integer)  # Optional population density


# National/local holiday table
class Holiday(db.Model):
    __tablename__ = "holiday"
    holiday_date = Column(
        Date, primary_key=True
    )  # Official holiday dates (affects predictions)


# Restaurant-level hourly popularity (historical)
class RestaurantPopularHour(db.Model):
    __tablename__ = "restaurant_popular_hour"
    place_id = Column(String, primary_key=True)  # Google place_id
    day = Column(String, primary_key=True)  # Day of week
    hour_0 = Column(Integer)  # Hourly popularity values from 0–23
    hour_1 = Column(Integer)
    hour_2 = Column(Integer)
    hour_3 = Column(Integer)
    hour_4 = Column(Integer)
    hour_5 = Column(Integer)
    hour_6 = Column(Integer)
    hour_7 = Column(Integer)
    hour_8 = Column(Integer)
    hour_9 = Column(Integer)
    hour_10 = Column(Integer)
    hour_11 = Column(Integer)
    hour_12 = Column(Integer)
    hour_13 = Column(Integer)
    hour_14 = Column(Integer)
    hour_15 = Column(Integer)
    hour_16 = Column(Integer)
    hour_17 = Column(Integer)
    hour_18 = Column(Integer)
    hour_19 = Column(Integer)
    hour_20 = Column(Integer)
    hour_21 = Column(Integer)
    hour_22 = Column(Integer)
    hour_23 = Column(Integer)


# Restaurant-level opening hours (binary per hour)
class RestaurantOpeningHour(db.Model):
    __tablename__ = "restaurant_opening_hour"
    restaurant_id = Column(
        UUID(as_uuid=True), ForeignKey("restaurants.restaurant_id"), primary_key=True
    )
    day = db.Column(db.String, primary_key=True)  # Day of week
    hour_0 = Column(Boolean)  # True/False flags for whether open
    hour_1 = Column(Boolean)
    hour_2 = Column(Boolean)
    hour_3 = Column(Boolean)
    hour_4 = Column(Boolean)
    hour_5 = Column(Boolean)
    hour_6 = Column(Boolean)
    hour_7 = Column(Boolean)
    hour_8 = Column(Boolean)
    hour_9 = Column(Boolean)
    hour_10 = Column(Boolean)
    hour_11 = Column(Boolean)
    hour_12 = Column(Boolean)
    hour_13 = Column(Boolean)
    hour_14 = Column(Boolean)
    hour_15 = Column(Boolean)
    hour_16 = Column(Boolean)
    hour_17 = Column(Boolean)
    hour_18 = Column(Boolean)
    hour_19 = Column(Boolean)
    hour_20 = Column(Boolean)
    hour_21 = Column(Boolean)
    hour_22 = Column(Boolean)
    hour_23 = Column(Boolean)


# Latest busyness level per grid (used for maps and overlays)
class LatestGridBusyness(db.Model):
    __tablename__ = "latest_grid_busyness"

    grid_id = Column(String, primary_key=True)  # Grid ID (one row per grid)
    predicted_level = Column(Integer, nullable=False)  # Most recent predicted level
    timestamp = Column(
        DateTime(timezone=True), nullable=False
    )  # When the prediction was made
    geometry = Column(
        Geometry("POLYGON"), nullable=True
    )  # Optional geo-shape of the grid

    def __repr__(self):
        return f"<LatestGridBusyness {self.grid_id} => {self.predicted_level} @ {self.timestamp}>"
