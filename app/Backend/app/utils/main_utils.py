# This file will hold helper functions for the backend.
# For now it's empty, but I will move reusable code here as needed.
import math  # Import math module for mathematical operations
import re  # Regular expression module for text normalization
from collections import defaultdict
from datetime import datetime, timedelta

import pandas as pd
import pytz
from app.models import (  # Import relevant SQLAlchemy models (used for potential future queries)
    BusynessPrediction, Restaurant)
from sqlalchemy import \
    func  # SQLAlchemy functions for aggregation (currently unused)
from sqlalchemy.orm import \
    Session  # SQLAlchemy session object (currently unused)


# Haversine distance function (to calculate distance between user and restaurant)
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371000  # Radius of Earth in meters
    phi1, phi2 = math.radians(lat1), math.radians(
        lat2
    )  # Convert latitude coordinates to radians
    delta_phi = math.radians(lat2 - lat1)  # Latitude difference in radians
    delta_lambda = math.radians(lon2 - lon1)  # Longitude difference in radians
    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )  # Haversine formula intermediate calculation
    c = 2 * math.atan2(
        math.sqrt(a), math.sqrt(1 - a)
    )  # Haversine formula arc calculation
    return R * c  # Return distance in meters between the two points


def normalize(text):
    """Replace all types of whitespace with a single space and lowercase."""
    return re.sub(r"\s+", " ", text).strip().lower()


# Maps numerical day to weekday name
WEEKDAY_MAP = {
    "0": "sunday",
    "1": "monday",
    "2": "tuesday",
    "3": "wednesday",
    "4": "thursday",
    "5": "friday",
    "6": "saturday",
}


# Format hour into readable string
def format_hour(hour: int) -> str:
    if hour == 24:
        return "12:00 AM"
    return datetime.strptime(f"{hour}:00", "%H:%M").strftime("%I:%M %p").lstrip("0")


# Compute contiguous open-close hour blocks from a list of True/False flags
def compute_intervals(hour_flags: list[bool]) -> list[tuple[int, int]]:
    """Return contiguous open-close hour blocks from list of True/False flags."""
    intervals = []
    start = None
    for hour, is_open in enumerate(hour_flags + [False]):
        if is_open and start is None:
            start = hour
        elif not is_open and start is not None:
            intervals.append((start, hour))
            start = None
    return intervals


# Get readable opening hours by day from database rows
def get_readable_hours_by_day(rows) -> dict:
    """Return dictionary of weekday -> opening hour string."""
    hours_by_day = {}

    for row in rows:
        hour_flags = [getattr(row, f"hour_{h}") for h in range(24)]
        intervals = compute_intervals(hour_flags)
        weekday = WEEKDAY_MAP.get(str(row.day), f"day_{row.day}")

        if intervals:
            readable = ", ".join(
                f"{format_hour(start)} – {format_hour(end)}" for start, end in intervals
            )
            hours_by_day[weekday] = readable
        else:
            hours_by_day[weekday] = "Closed"

    return hours_by_day


# Timezones
NY_TZ = pytz.timezone("America/New_York")
UTC_TZ = pytz.utc


# Convert naive New York time to UTC-aware datetime
def ny_to_utc(ny_time: datetime) -> datetime:
    """
    Convert a naive datetime that represents New York local time
    into a UTC-aware datetime for database queries.
    """
    if ny_time.tzinfo is None:
        ny_time = NY_TZ.localize(ny_time)  # assume input is NY local
    return ny_time.astimezone(UTC_TZ)


# Convert UTC-aware datetime to New York local time
def utc_to_ny(utc_time: datetime) -> datetime:
    """
    Convert a UTC datetime from the database into New York local time.
    """
    if utc_time.tzinfo is None:
        utc_time = UTC_TZ.localize(utc_time)
    return utc_time.astimezone(NY_TZ)


# Get current time in New York timezone
def get_current_time_ny() -> datetime:
    """Get the current New York time."""
    return datetime.now(NY_TZ)
