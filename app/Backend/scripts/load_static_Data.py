import ast
import json
import os
from io import StringIO
from pathlib import Path

import pandas as pd
import psycopg2
from db_utils import *  # Custom utility for upsert operations
from dotenv import load_dotenv  # Load DB connection string
from sqlalchemy import Table  # SQLAlchemy core components
from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.dialects.postgresql import \
    insert  # Enables UPSERT via PostgreSQL syntax

# Load environment variables from .env
load_dotenv()

# Read the database URL from the environment
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL not found in .env")

# Create SQLAlchemy engine using Supabase PostgreSQL connection
engine = create_engine(DATABASE_URL)

# ---------- Loaders ----------


def load_location_df():
    """
    Loads 'location_df.csv' into the 'location_mapping' table.
    Converts WKT geometries to string before load.
    """
    print("→ Loading location_df.csv...")
    df = pd.read_csv("app/data/data_preparation/prepared_outputs/location_df.csv")

    # Ensure geometry column is a string (WKT)
    if "geometry" in df.columns:
        df["geometry"] = df["geometry"].astype(str)

    # Overwrite table with new data
    df.to_sql("location_mapping", con=engine, if_exists="replace", index=False)
    print("location_mapping loaded.")


def load_grid_info():
    """
    Loads 'grid_info.csv' and performs an UPSERT into the 'grid_info' table.
    Geometry is stringified, and 'weighted' column is dropped if present.
    """
    print("→ Loading grid_info.csv...")
    df = pd.read_csv("app/data/data_preparation/prepared_outputs/grid_info.csv")

    # Drop unused or legacy column
    df.drop(columns=["weighted"], errors="ignore", inplace=True)

    if "geometry" in df.columns:
        df["geometry"] = df["geometry"].astype(str)

    # Reflect existing table structure
    metadata = MetaData()
    grid_info_table = Table("grid_info", metadata, autoload_with=engine)

    # Perform UPSERT using PostgreSQL insert with conflict resolution
    with engine.begin() as conn:
        for _, row in df.iterrows():
            stmt = (
                insert(grid_info_table)
                .values(
                    grid_id=row["grid_id"],
                    lat=row["lat"],
                    lon=row["lon"],
                    geometry=row["geometry"],
                    restaurant_count=row["restaurant_count"],
                    population=row["population"],
                )
                .on_conflict_do_update(
                    index_elements=["grid_id"],
                    set_={
                        "lat": row["lat"],
                        "lon": row["lon"],
                        "geometry": row["geometry"],
                        "restaurant_count": row["restaurant_count"],
                        "population": row["population"],
                    },
                )
            )
            conn.execute(stmt)

    print("grid_info upserted.")


def load_holiday():
    """
    Loads 'holiday_df.csv' directly into the 'holiday' table.
    """
    print("→ Loading holiday_df.csv...")
    df = pd.read_csv("app/data/data_preparation/prepared_outputs/holiday_df.csv")
    df.to_sql("holiday", con=engine, if_exists="replace", index=False)
    print("holiday loaded.")


from io import StringIO

import pandas as pd
import psycopg2


def load_restaurant_opening_hour():
    """
    Loads restaurant_opening_hour.csv into the restaurant_opening_hour table
    but only populates the columns present in the CSV (leaves out restaurant_id).
    Data is inserted in manageable chunks to avoid statement timeouts.
    """
    print("→ Loading restaurant_opening_hour.csv")

    path = (
        "app/data/data_preparation/restaurant_data_fetching/restaurant_opening_hour.csv"
    )
    df = pd.read_csv(path)

    if "geometry" in df.columns:
        df["geometry"] = df["geometry"].astype(str)

    column_list = [
        "full_name",
        "day",
        "hour_0",
        "hour_1",
        "hour_2",
        "hour_3",
        "hour_4",
        "hour_5",
        "hour_6",
        "hour_7",
        "hour_8",
        "hour_9",
        "hour_10",
        "hour_11",
        "hour_12",
        "hour_13",
        "hour_14",
        "hour_15",
        "hour_16",
        "hour_17",
        "hour_18",
        "hour_19",
        "hour_20",
        "hour_21",
        "hour_22",
        "hour_23",
    ]

    columns_sql = ",".join(column_list)
    copy_sql_header = (
        f"COPY restaurant_opening_hour ({columns_sql}) FROM STDIN WITH CSV HEADER"
    )
    copy_sql_no_header = (
        f"COPY restaurant_opening_hour ({columns_sql}) FROM STDIN WITH CSV"
    )

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE restaurant_opening_hour;")
    conn.commit()

    chunksize = 5000  # tune this if still hitting timeouts
    total_rows = len(df)
    for start in range(0, total_rows, chunksize):
        end = min(start + chunksize, total_rows)
        chunk = df.iloc[start:end]

        buffer = StringIO()
        # Only write header for first chunk
        chunk.to_csv(buffer, index=False, header=(start == 0))
        buffer.seek(0)

        # Pick correct COPY SQL
        sql = copy_sql_header if start == 0 else copy_sql_no_header
        cur.copy_expert(sql, buffer)
        conn.commit()
        print(f"Inserted rows {start}–{end}")

    cur.close()
    conn.close()
    print("restaurant_opening_hour loaded successfully")


def load_restaurant():
    """
    Loads restaurant_info.csv into temp_restaurants with proper types,
    then upserts into restaurants with ON CONFLICT(full_name) DO UPDATE.
    Normalizes full_name to lowercase to prevent duplicates by casing.
    """
    print("\n→ Loading restaurant_info.csv with fast COPY...")
    path = "app/data/data_preparation/prepared_outputs/restaurant_info.csv"
    df = pd.read_csv(path)
    print("DEBUG: Original CSV columns:", df.columns.tolist())

    # Normalize columns
    df.columns = [c.lower() for c in df.columns]

    # Normalize full_name for consistency (avoid duplicates with case differences)
    def normalize_name(name):
        if pd.isna(name):
            return None
        name = re.sub(r"[^\w\s]", "", name)  # remove punctuation like , . etc
        name = re.sub(r"\s+", " ", name)  # collapse multiple spaces
        return name.strip().upper()

    df["full_name"] = df["full_name"].apply(normalize_name)
    df = df.drop_duplicates(subset=["full_name"], keep="first")

    # Rename column for schema
    if "opening_hour" in df.columns:
        df.rename(columns={"opening_hour": "opening_hours"}, inplace=True)

    # Geometry as string
    if "geometry" in df.columns:
        df["geometry"] = df["geometry"].astype(str)

    # Floats
    for col in ["lat", "lon"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Integers
    if "review_count" in df.columns:
        df["review_count"] = (
            pd.to_numeric(df["review_count"], errors="coerce")
            .fillna(0)
            .round()
            .astype("Int64")
        )

    if "price_level" in df.columns:
        price_map = {"$": 1, "$$": 2, "$$$": 3, "$$$$": 4}
        df["price_level"] = (
            df["price_level"]
            .apply(
                lambda x: (
                    price_map[x]
                    if x in price_map
                    else (
                        int(float(x))
                        if pd.notna(x) and str(x).replace(".", "", 1).isdigit()
                        else None
                    )
                )
            )
            .astype("Int64")
        )

    # Boolean
    if "wheelchair_friendly" in df.columns:

        def to_bool(val):
            if pd.isna(val):
                return None
            val_str = str(val).strip().lower()
            if val_str in {"1", "1.0", "true", "t", "yes"}:
                return True
            if val_str in {"0", "0.0", "false", "f", "no"}:
                return False
            return None

        df["wheelchair_friendly"] = df["wheelchair_friendly"].apply(to_bool)

    # Drop rows with missing full_name,
    if "full_name" in df.columns:
        before_count = len(df)
        df = df[df["full_name"].notna()]
        df["full_name"] = df["full_name"].str.strip().str.upper()
        df = df.drop_duplicates(subset=["full_name"], keep="first")
        after_count = len(df)
        print(
            f"Removed {before_count - after_count} rows (missing or duplicate full_name)."
        )

    # Fix JSON fields
    for json_col in ["opening_hours", "cuisine_keyword", "amenities"]:
        if json_col in df.columns:
            print(f"Fixing JSON for {json_col}…")
            df[json_col] = df[json_col].apply(force_json)
            sample = df[json_col].dropna()
            if not sample.empty:
                print(f"Sample after fix in {json_col}:", sample.iloc[0])

    # Truncate staging table
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE temp_restaurants;")
    conn.commit()

    # COPY in chunks
    cols_sql = ",".join(df.columns)
    sql_header = f"COPY temp_restaurants ({cols_sql}) FROM STDIN WITH CSV HEADER"
    sql_no_header = f"COPY temp_restaurants ({cols_sql}) FROM STDIN WITH CSV"

    chunksize = 1000
    total_rows = len(df)
    for start in range(0, total_rows, chunksize):
        end = min(start + chunksize, total_rows)
        buf = StringIO()
        df.iloc[start:end].to_csv(buf, index=False, header=(start == 0))
        buf.seek(0)
        cur.copy_expert(sql_header if start == 0 else sql_no_header, buf)
        conn.commit()
        print(f" Inserted rows {start}–{end}")

    cur.close()
    conn.close()
    print("Finished COPY into temp_restaurants")

    # Upsert with update into restaurants
    upsert_from_temp_table(
        temp_table="temp_restaurants",
        target_table="restaurants",
        conflict_cols=["full_name"],  # uses ON CONFLICT(full_name) DO UPDATE
        engine=engine,
    )

    print("restaurant_info loaded and upserted successfully!")


# ---------- Main Runner ----------


def main():
    """
    Master function that loads all static CSVs into Supabase in order.
    """
    print("Loading static datasets into Supabase...\n")
    load_location_df()
    load_grid_info()
    load_holiday()
    load_restaurant_opening_hour()
    load_restaurant()
    print("\n All datasets loaded successfully!")


# Run script only if executed directly (not on import)
if __name__ == "__main__":
    main()
