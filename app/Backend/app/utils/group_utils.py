import math
from typing import Dict, List, Tuple

from app.utils.main_utils import haversine_distance


def calculate_group_fit_score(
    r, prediction, group_preferences: List[Dict], user_lat: float, user_lon: float
) -> Tuple[float, float]:
    """
    Calculates the group fit score for a restaurant based on individual user preferences.

    NOW INCLUDES PRICE LEVEL FACTOR.

    Factors and weights:
    --------------------
    - Cuisine match as a simple yes/no (weighted 40%)
    - Distance tolerance (weighted 20%)
    - Busyness tolerance (weighted 15%)
    - Restaurant rating vs. user minimum_rating (weighted 10%)
    - Price level match (weighted 15%)

    Parameters
    ----------
    r : Restaurant SQLAlchemy object
        Fields used:
            r.lat, r.lon, r.cuisine_keyword, r.rating, r.price_level (1–3)

    prediction : BusynessPrediction object
        Field used:
            prediction.predicted_level (1–5)

    group_preferences : list of dict
        Each dict should include:
        {
            "cuisine_preferences": [<cuisine_name_lower>, ...],
            "distance_preference": <int 1–5>,
            "busyness_preference": <int 1–5>,
            "minimum_rating": <float>,         # optional
            "price_level": <int 1–3>           # optional
        }

    user_lat : float
        Average latitude of the group

    user_lon : float
        Average longitude of the group

    Returns
    -------
    (fit_score, distance_meters)
        fit_score : float in [0.0, 1.0]
        distance_meters : float (raw distance)
    """

    # If no preferences, no fit
    if not group_preferences:
        return 0.0, 0.0

    # -----------------------
    # DISTANCE CALCULATION
    # -----------------------
    distance_meters = haversine_distance(user_lat, user_lon, r.lat, r.lon)

    # -----------------------
    # NORMALIZED BUSYNESS
    # -----------------------
    predicted_busyness = (prediction.predicted_level - 1) / 4.0  # 1–5 → 0–1

    # -----------------------
    # NORMALIZED CUISINE LIST
    # -----------------------
    restaurant_cuisines = [
        c["title"].strip().lower() for c in (r.cuisine_keyword or [])
    ]

    # -----------------------
    # PRICE LEVEL FROM RESTAURANT
    # -----------------------
    restaurant_price_level = (
        r.price_level if hasattr(r, "price_level") and r.price_level else None
    )

    total_dissatisfaction = 0.0

    # Loop over each user's preferences
    for user in group_preferences:
        # -----------------------
        # CUISINE DISSATISFACTION (YES/NO)
        # -----------------------
        user_cuisines = set(c.lower() for c in user.get("cuisine_preferences", []))
        if not user_cuisines:
            # No preference given → neutral dissatisfaction
            cuisine_dissatisfaction = 0.5
        else:
            # If ANY of the restaurant's cuisines are in user's preferences → good match
            cuisine_dissatisfaction = (
                0.0 if any(c in user_cuisines for c in restaurant_cuisines) else 1.0
            )

        # ------------------------
        # DISTANCE DISSATISFACTION
        # ------------------------
        dist_pref = user.get("distance_preference", 3)
        distance_tolerance_scale = max(0.1, (6 - dist_pref) / 5.0)
        distance_dissatisfaction = (distance_meters / 500.0) * distance_tolerance_scale
        distance_dissatisfaction = min(distance_dissatisfaction, 1.0)

        # -------------------------
        # BUSYNESS DISSATISFACTION
        # -------------------------
        busyness_target = (user.get("busyness_preference", 3) - 1) / 4.0
        busyness_dissatisfaction = abs(predicted_busyness - busyness_target)

        # ----------------------
        # RATING DISSATISFACTION
        # ----------------------
        minimum_rating = user.get("minimum_rating", 0.0)
        if r.rating is not None:
            if r.rating < minimum_rating:
                rating_dissatisfaction = min(1.0, (minimum_rating - r.rating) / 5.0)
            else:
                rating_dissatisfaction = 0.0
        else:
            rating_dissatisfaction = 0.0

        # ----------------------
        # PRICE LEVEL DISSATISFACTION
        # ----------------------
        if restaurant_price_level is not None:
            preferred_price = user.get("price_level")
            if preferred_price is not None:
                diff = abs(
                    restaurant_price_level - preferred_price
                )  # max diff is 2 (1 vs 3)
                price_dissatisfaction = min(diff / 2.0, 1.0)
            else:
                # If user gave no price preference → neutral dissatisfaction
                price_dissatisfaction = 0.5
        else:
            # If restaurant has no price info → neutral dissatisfaction
            price_dissatisfaction = 0.5

        # ----------------------
        # COMBINE WITH WEIGHTS
        # ----------------------
        user_dissatisfaction = (
            0.40 * cuisine_dissatisfaction
            + 0.20 * distance_dissatisfaction
            + 0.15 * busyness_dissatisfaction
            + 0.10 * rating_dissatisfaction
            + 0.15 * price_dissatisfaction
        )

        total_dissatisfaction += user_dissatisfaction

    # -----------------------
    # AVERAGE ACROSS USERS
    # -----------------------
    avg_dissatisfaction = total_dissatisfaction / len(group_preferences)

    # -----------------------
    # CONVERT DISSATISFACTION INTO FIT SCORE
    # -----------------------
    fit_score = 1 / (1 + avg_dissatisfaction)
    fit_score = max(0.0, min(1.0, fit_score))

    return fit_score, distance_meters
