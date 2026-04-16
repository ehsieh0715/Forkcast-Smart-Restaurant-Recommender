import ast
import json
import os
import re
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# ------------------ Load environment ------------------

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL not found in .env")

engine = create_engine(DATABASE_URL)

# ------------------ Type Resolver ------------------


def get_postgres_type(col_name: str) -> str:
    """
    Map pandas column names to PostgreSQL types.
    Update this mapping if your schema evolves.
    """
    float_cols = {
        "lat",
        "lon",
        "lat_rounded",
        "lon_rounded",
        "rating",
        "price_level",
        "restaurant_counts",
        "distance_to_fairfax",
        "distance_to_stella_34_trattoria",
        "distance_to_old_homestead_steakhouse",
    }
    int_cols = {"review_count"}
    bool_cols = {
        "has_opening_hour_data",
        "has_popular_hour_data",
        "wheelchair_friendly",
    }
    date_cols = {"inspection_date"}
    json_cols = {"opening_hours", "cuisine_keyword", "amenities"}

    if col_name in float_cols:
        return "float"
    elif col_name in int_cols:
        return "int"
    elif col_name in bool_cols:
        return "boolean"
    elif col_name in date_cols:
        return "date"
    elif col_name in json_cols:
        return "jsonb"
    elif col_name == "geometry":
        return "text"
    else:
        # default to text for unknowns
        return "text"


# ------------------ Upsert Function ------------------


def upsert_from_temp_table(
    temp_table: str, target_table: str, conflict_cols: list, engine=None
):
    """
    Upsert data from temp_table into target_table:
    - Inserts new rows
    - Updates all non-conflict columns if a duplicate is found
    """
    if engine is None:
        raise ValueError("Engine must be provided.")

    # Reflect available columns from the temp table
    with engine.begin() as conn:
        result = conn.execute(text(f"SELECT * FROM {temp_table} LIMIT 0"))
        columns = result.keys()

    print("TEMP TABLE COLUMNS:", list(columns))

    # Build insert column list
    insert_cols = ", ".join(columns)

    # Build SELECT with casts
    cast_expr = ",\n        ".join(
        [f"{col}::{get_postgres_type(col)}" for col in columns]
    )

    # Build update set expressions (exclude conflict columns)
    update_set = ",\n        ".join(
        [f"{col} = EXCLUDED.{col}" for col in columns if col not in conflict_cols]
    )

    conflict_clause = ", ".join(conflict_cols)

    stmt = f"""
        INSERT INTO {target_table} (
            {insert_cols}
        )
        SELECT
            {cast_expr}
        FROM {temp_table}
        ON CONFLICT ({conflict_clause}) DO UPDATE SET
            {update_set};
    """

    with engine.begin() as conn:
        conn.execute(text(stmt))
        print(f"Upsert with update from {temp_table} to {target_table} complete.")


def force_json(val):
    if pd.isna(val):
        return None
    if isinstance(val, (dict, list)):
        return json.dumps(val)
    try:
        parsed = ast.literal_eval(str(val))
        return json.dumps(parsed)
    except Exception:
        # fallback: naive single-quote replacement
        return str(val).replace("'", '"')


def normalize_name(name):
    if pd.isna(name):
        return None
    name = re.sub(r"[^\w\s]", "", name)  # remove punctuation like , . etc
    name = re.sub(r"\s+", " ", name)  # collapse multiple spaces
    return name.strip().upper()
