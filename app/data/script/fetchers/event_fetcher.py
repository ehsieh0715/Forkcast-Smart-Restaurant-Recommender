import datetime
import os
import re
import time
from urllib.parse import quote

import geopandas as gpd
import osmnx as ox
import pandas as pd
import requests
from dotenv import load_dotenv
from geopy.geocoders import Nominatim
from shapely.geometry import Point
from shapely.wkt import dumps
from supabase_utils.supabase_client import SupabaseClient

load_dotenv()


class EventDataFetcher:
    """
    Class responsible for fetching and processing NYC event data,
    including geocoding, spatial joins with Manhattan grids, and
    transforming event data into hourly grid-level counts.
    """

    def __init__(self, target_datetime: datetime):
        """
        Initialize with target datetime.

        Args:
            target_datetime (datetime): Target time to fetch event data (rounded to the nearest hour).
        """
        self.target_datetime = pd.to_datetime(target_datetime).round("h")
        self.supabase_client = SupabaseClient()

    def fetch_hourly_events_manhattan(self, target_datetime):
        """
        Fetch events from NYC Open Data API that overlap with the given hour and are located in Manhattan.

        Args:
            target_datetime (datetime): The datetime to query for events.

        Returns:
            pd.DataFrame: DataFrame of raw events.
        """
        start_time = target_datetime
        end_time = start_time + pd.Timedelta(hours=1)

        s_iso = start_time.strftime("%Y-%m-%dT%H:%M:%S")
        e_iso = end_time.strftime("%Y-%m-%dT%H:%M:%S")

        where_clause = f"""
            SELECT
            event_id,
            start_date_time AS start_time,
            end_date_time AS end_time,
            event_location
            WHERE
            (start_date_time <= "{e_iso}" :: floating_timestamp)
            AND (end_date_time >= "{s_iso}" :: floating_timestamp)
            AND caseless_one_of(event_borough, "Manhattan")
            GROUP BY event_id, start_date_time, end_date_time, event_location
        """
        encoded_query = quote(where_clause, safe="")
        url = f"https://data.cityofnewyork.us/resource/tvpp-9vvx.json?$query={encoded_query}"

        response = requests.get(url)
        if response.status_code == 200:
            raw_event_df = pd.DataFrame(response.json())
            print(f"✅ Fetched {raw_event_df.shape[0]} events.")
            return raw_event_df
        else:
            print(f"❌ Failed to fetch events: HTTP {response.status_code}")
            return pd.DataFrame()

    def extract_main_location(self, text):
        """
        Extract the primary location name from a full location string.

        Args:
            text (str): Raw location string.

        Returns:
            str: Cleaned main location.
        """
        match_colon = re.match(r"^(.*?):", text)
        if match_colon:
            return match_colon.group(1).strip()
        match_between = re.match(r"^(.*?)\s+between\s+", text, re.IGNORECASE)
        if match_between:
            return match_between.group(1).strip()
        return text

    def standardize_address(self, text):
        """
        Convert street address to a standardized form for geocoding.

        Args:
            text (str): Raw location string.

        Returns:
            str: Standardized location string.
        """
        text = text.upper()
        text = text.replace("WEST", "W")
        text = text.replace("EAST", "E")
        text = text.replace("STREET", "St")
        text = text.replace("AVENUE", "Ave")
        text = text.replace(" BOULEVARD", " Blvd")
        text = text.replace(" PLACE", " Pl")
        text = text.replace(" ROAD", " Rd")
        text = text.replace(" CIRCLE", " Cir")
        return text

    def geocode_missing_geometry_osm(self, location_df, location_col):
        """
        Geocode missing geometries using OpenStreetMap.

        Args:
            location_df (pd.DataFrame): Data with 'geometry' column and location info.
            location_col (str): Column containing cleaned location names.

        Returns:
            pd.DataFrame: Updated DataFrame with filled geometries.
        """
        # Identify rows missing geometry before resolution
        missing_geometry_df = location_df[location_df["geometry"].isna()]
        num_missing_before = missing_geometry_df.shape[0]
        print(
            f"🔍 Geometry missing before OpenStreetMap resolution: {num_missing_before}"
        )

        # Resolve missing geometries
        for i, row in missing_geometry_df.iterrows():
            geom, src = self.get_event_geometry(row[location_col])
            location_df.at[i, "geometry"] = geom
            location_df.at[i, "source_type"] = src
            print(i, row["main_location"], geom, src)

        # Count how many are still missing after resolution
        num_missing_after = location_df["geometry"].isna().sum()
        num_fixed = num_missing_before - num_missing_after
        print(f"Geometry fixed: {num_fixed}")
        print(f"Still missing after attempt: {num_missing_after}")
        return location_df

    def geocode_missing_geometry_google(
        self,
        location_df,
        location_col="fixed_main_location",
        api_key=None,
        buffer_radius_m=200,
        sleep_time=1.0,
    ):
        """
        Geocode missing geometries using Google Maps API.

        Args:
            location_df (pd.DataFrame): DataFrame with missing geometries.
            location_col (str): Column with standardized location names.
            api_key (str): Google Maps API key.
            buffer_radius_m (float): Radius to buffer around point.
            sleep_time (float): Delay between API calls.

        Returns:
            pd.DataFrame: DataFrame with geometry filled.
        """
        assert api_key, "Google Maps API key (api_key) is required."
        buffer_radius_deg = buffer_radius_m / 111000  # ~1 degree ≈ 111 km

        # Identify rows missing geometry before resolution
        missing_geometry_df = location_df[location_df["geometry"].isna()]
        num_missing_before = missing_geometry_df.shape[0]
        print(
            f"🔍 Geometry missing before Google Maps API resolution: {num_missing_before}"
        )

        for i, row in missing_geometry_df.iterrows():
            try:
                query = f"{row[location_col]}, Manhattan, New York, NY"
                url = f"https://maps.googleapis.com/maps/api/geocode/json?address={query}&key={api_key}"
                response = requests.get(url).json()

                if response["status"] == "OK" and response["results"]:
                    location = response["results"][0]["geometry"]["location"]
                    lat, lon = location["lat"], location["lng"]
                    point = Point(lon, lat)
                    location_df.at[i, "geometry"] = point.buffer(buffer_radius_deg)
                    location_df.at[i, "source_type"] = "google"

                    print(f"{i}: {query} → ({lat}, {lon})")
                else:
                    print(f"❌ Could not resolve location: {query}")
            except Exception as e:
                print(f"⚠️ Error @ {row[location_col]}: {e}")

            time.sleep(sleep_time)

        # Count how many are still missing after resolution
        num_missing_after = location_df["geometry"].isna().sum()
        num_fixed = num_missing_before - num_missing_after
        print(f"Geometry fixed: {num_fixed}")
        print(f"Still missing after attempt: {num_missing_after}")

        return location_df

    def gen_area_area_mapping(self, zone_df, grid_df, zone_location_id):
        """
        Generate mapping between zone polygons and spatial grid cells.

        Args:
            zone_df (gpd.GeoDataFrame): GeoDataFrame of zone geometries.
            grid_df (gpd.GeoDataFrame): GeoDataFrame of grid geometries.
            zone_location_id (str): Column name identifying zone.

        Returns:
            gpd.GeoDataFrame: Mapping from zone to grid_id.
        """
        # Make copies to avoid modifying original dataframes
        zone_gdf = zone_df.copy()
        grid_gdf = grid_df.copy()

        # Ensure 'geometry' is set as the active geometry column
        zone_gdf = zone_gdf.set_geometry("geometry")
        grid_gdf = grid_gdf.set_geometry("geometry")

        # Standardize both GeoDataFrames to WGS84 (EPSG:4326) for consistency
        zone_gdf = zone_gdf.to_crs("EPSG:4326")
        grid_gdf = grid_gdf.to_crs("EPSG:4326")

        # Perform a spatial join to find all grid cells that intersect each zone
        # Returns pairs of (grid_id, zone_id) where geometries overlap
        zone_to_grid = gpd.sjoin(
            grid_gdf[["grid_id", "geometry"]],
            zone_gdf[[zone_location_id, "geometry"]],
            how="inner",
            predicate="intersects",
        )

        return zone_to_grid

    def resolve_event_geometry(self, raw_event_df):
        """
        Resolve geometries for events using cached, OSM, and Google APIs.

        Args:
            raw_event_df (pd.DataFrame): Raw events with 'main_location'.

        Returns:
            pd.DataFrame: Events with resolved geometry.
        """
        # Step 1: Match raw events to cached location-to-geometry records
        location_df = self.supabase_client.fetch_all(table_name="location_mapping")
        print("📌 Columns in location_df:", location_df.columns.tolist())
        if (
            "main_location" not in location_df.columns
            or "geometry" not in location_df.columns
        ):
            print("❌ 'main_location' or 'geometry' missing in location_mapping table!")
            print("🔁 Returning raw_event_df for inspection.")
            return raw_event_df

        raw_event_df["main_location"] = raw_event_df["event_location"].apply(
            self.extract_main_location
        )
        event_df = raw_event_df.merge(
            location_df[["main_location", "geometry"]], on="main_location", how="left"
        )

        # Step 2: Geocode unmatched locations using OSM (Nominatim)
        event_df["fixed_main_location"] = event_df["main_location"].apply(
            self.standardize_address
        )
        event_df = self.geocode_missing_geometry_osm(
            location_df=event_df, location_col="fixed_main_location"
        )

        # Step 3: Fallback to Google Maps API for still-unresolved locations
        load_dotenv()
        google_api_key = os.getenv("GOOGLE_API_KEY")
        event_df = self.geocode_missing_geometry_google(
            location_df=event_df, location_col="main_location", api_key=google_api_key
        )

        # Step 4: Drop records that still lack valid geometry after both geocoding attempts
        event_df = event_df[event_df["geometry"].notna()]

        # Step 5: Cache newly resolved main_location → geometry pairs to Supabase
        new_location_df = event_df[
            ~event_df["main_location"].isin(location_df["main_location"])
        ][["main_location", "geometry"]]

        # Avoid uploading if no new locations were resolved
        if new_location_df.shape[0] > 0:
            new_location_df["geometry"] = new_location_df["geometry"].apply(dumps)
            self.supabase_client.insert_all(
                table_name="location_mapping", df=new_location_df
            )
        return event_df

    def expand_event_to_hourly_grid(self, merged_event_df):
        """
        Expand event records into hourly grid-level counts.

        Args:
            merged_event_df (pd.DataFrame): Events with 'grid_id', 'start_time', 'end_time'.

        Returns:
            pd.DataFrame: Hourly counts per grid.
        """
        expanded_rows = []
        for _, row in merged_event_df.iterrows():
            hours = pd.date_range(
                start=row["start_time"], end=row["end_time"], freq="h"
            )
            for h in hours:
                expanded_rows.append({"event_hour": h, "grid_id": row["grid_id"]})

        hourly_df = pd.DataFrame(expanded_rows)
        hourly_df["event_rounded_hour"] = hourly_df["event_hour"].dt.floor("h")
        hourly_count = (
            hourly_df.groupby(["event_rounded_hour", "grid_id"])
            .size()
            .reset_index(name="event_count")
        )
        hourly_count["date"] = hourly_count["event_rounded_hour"].dt.date
        hourly_count["hour"] = hourly_count["event_rounded_hour"].dt.hour.astype(int)
        return hourly_count

    def get_hourly_grid_event(self):
        """
        Full pipeline: fetch → geocode → spatial join → expand → summarize events.

        Returns:
            pd.DataFrame: Grid-level hourly event counts with date and hour.
        """
        # Step 1: Fetch raw events that overlap with the target hourly window
        raw_event_df = self.fetch_hourly_events_manhattan(self.target_datetime)

        # Step 2: Resolve location geometry using cached data, OSM, and Google Maps APIs
        event_df = self.resolve_event_geometry(raw_event_df)

        # Step 3: Load spatial grid of Manhattan divided into grid cells
        grid_df = self.supabase_client.fetch_all("grid_info")

        # Step 4: Identify which grid cells each event intersects with (zone-to-grid mapping)
        event_zone = event_df[["main_location", "geometry"]].drop_duplicates()
        event_zone_to_grid = self.gen_area_area_mapping(
            zone_df=event_zone, grid_df=grid_df, zone_location_id="main_location"
        )

        # Step 5: Assign grid IDs to each event based on spatial join results
        merged_event_df = event_df.merge(
            event_zone_to_grid[["main_location", "grid_id"]], on="main_location"
        )
        merged_event_df["start_time"] = pd.to_datetime(merged_event_df["start_time"])
        merged_event_df["end_time"] = pd.to_datetime(merged_event_df["end_time"])

        # Step 6: Expand event durations into hourly time slots and count how many events per grid per hour
        event_hourly_count = self.expand_event_to_hourly_grid(merged_event_df)

        # Step 7: Filter the expanded event counts to only include rows matching the target hour
        start_time = pd.to_datetime(self.target_datetime).round("h")
        end_time = start_time + pd.Timedelta(hours=1)
        target_event_df = event_hourly_count[
            (event_hourly_count["event_rounded_hour"] >= start_time)
            & (event_hourly_count["event_rounded_hour"] < end_time)
        ]
        return target_event_df[["grid_id", "event_count", "date", "hour"]]

    def get_event_geometry(self, location_string, buffer_radius_deg=200):
        """
        Geocode a single location string and return a Polygon geometry.

        Args:
            location_string (str): The full address or place name to geocode.
            buffer_radius_deg (float): Buffer radius in degrees for fallback; approx 1 degree ≈ 111 km.

        Returns:
            geometry (shapely Polygon or None): The resulting area geometry.
            source (str or None): 'polygon' if from OSMnx, 'OSM' if from buffered Point, None if failed.
        """
        geolocator = Nominatim(user_agent="event_geocoder")

        # First try OSMnx for Polygon / MultiPolygon boundaries
        try:
            gdf = ox.geocode_to_gdf(location_string)
            if not gdf.empty:
                geom = gdf.geometry.iloc[0]
                if geom.geom_type in ["Polygon", "MultiPolygon"]:
                    return geom, "polygon"
        except Exception:
            pass

        # Fallback: Use geopy to retrieve Point and buffer to approximate area
        try:
            location = geolocator.geocode(location_string)
            if location:
                lat, lon = location.latitude, location.longitude
                point = Point(lon, lat)
                polygon = point.buffer(buffer_radius_deg)
                return polygon, "OSM"
        except Exception as e:
            print(f"⚠️ Geocoding failed for '{location_string}': {e}")

        # If all attempts fail, return None
        return None, None


if __name__ == "__main__":
    now_ts = pd.Timestamp(datetime.datetime.now()).round("h")
    now_dt = now_ts.to_pydatetime()

    # Run test case: fetch hourly event count for current time
    print("Test Case – Hourly Events at:", now_dt)
    fetcher = EventDataFetcher(target_datetime=now_dt)
    result = fetcher.get_hourly_grid_event()
    print(result.head())
