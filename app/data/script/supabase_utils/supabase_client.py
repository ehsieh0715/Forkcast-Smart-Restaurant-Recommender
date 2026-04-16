import os
import traceback

import geopandas as gpd
import pandas as pd
from dotenv import load_dotenv
from shapely import wkt  # ⬅️ Use this instead of wkb
from shapely.geometry import shape
from supabase import create_client

load_dotenv()


class SupabaseClient:
    """
    A client wrapper for interacting with Supabase tables, supporting both standard
    tabular data and geospatial data with WKT or GeoJSON-style geometries.
    """

    def __init__(self, url=None, key=None):
        """
        Initialize the Supabase client using credentials from environment variables
        or explicitly passed parameters.
        """
        if url is None or key is None:
            load_dotenv()
            url = url or os.getenv("SUPABASE_URL")
            key = key or os.getenv("SUPABASE_KEY")
        self.supabase = create_client(url, key)

    def _parse_geometry(self, x):
        """
        Convert geometry values from Supabase into shapely geometry objects.

        Args:
            x (str or dict): A geometry in WKT format or GeoJSON-like dict.

        Returns:
            shapely.geometry.base.BaseGeometry or None
        """
        try:
            if isinstance(x, str):
                return wkt.loads(x)  # ✅ Fixed to use WKT
            elif isinstance(x, dict):
                return shape(x)
            else:
                return None
        except Exception as e:
            print(f"⚠️ Failed to parse geometry: {x} – {e}")
            return None

    def fetch_all(self, table_name):
        """
        Try fetching from Supabase; fallback to local file if offline or empty.
        """
        try:
            response = self.supabase.table(table_name).select("*").execute()
            df = pd.DataFrame(response.data)

            # If Supabase returns empty, fallback to local
            if df.empty:
                raise ValueError("Supabase returned empty dataframe")

            if "geometry" in df.columns:
                df["geometry"] = df["geometry"].apply(self._parse_geometry)
                gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")
                return gdf
            return df

        except Exception as e:
            print(f"⚠️ Supabase fetch failed for '{table_name}': {e}")
            print("🔁 Trying fallback from local files...")

            # Fallback mapping — matches your current file locations
            fallback_paths = {
                "location_mapping": "data/save_to_database/location_df.csv",
                "grid_info": "data/save_to_database/grid_info.csv",
                "holiday": "data/save_to_database/holiday_df.csv",
            }

            fallback_path = fallback_paths.get(table_name)

            if fallback_path and os.path.exists(fallback_path):
                if table_name in ["grid_info", "location_mapping"]:
                    df = pd.read_csv(fallback_path)
                    df["geometry"] = df["geometry"].apply(self._parse_geometry)
                    return gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")
                else:
                    return pd.read_csv(fallback_path)
            else:
                print(f"❌ No fallback file found for {table_name}")
                return pd.DataFrame()

    def insert_all(self, table_name: str, df: pd.DataFrame, upsert: bool = True):
        """
        Insert or upsert rows into a Supabase table from a DataFrame.

        Args:
            table_name (str): Name of the Supabase table.
            df (pd.DataFrame): DataFrame of rows to insert or upsert.
            upsert (bool): If True (default), performs upsert. If False, performs plain insert.
        """
        records = df.copy().to_dict(orient="records")
        for i in range(0, len(records), 100):
            chunk = records[i : i + 100]
            try:
                table = self.supabase.table(table_name)
                if upsert:
                    resp = table.upsert(chunk).execute()
                else:
                    resp = table.insert(chunk).execute()
                if getattr(resp, "error", None):
                    print(
                        f"❌ {('Upsert' if upsert else 'Insert')} chunk {i}-{i+len(chunk)-1} failed:",
                        resp.error,
                    )
                else:
                    print(
                        f"✅ {('Upserted' if upsert else 'Inserted')} chunk {i}-{i+len(chunk)-1}"
                    )
            except Exception as e:
                print(f"❌ Failed to process chunk {i}-{i+len(chunk)-1}: {e}")
        print(f"✅ {('Upserted' if upsert else 'Inserted')} {len(records)} rows")


if __name__ == "__main__":
    print("🔍 Testing Supabase fetch for 'holiday' table...")
    supabase = SupabaseClient()
    holiday_df = supabase.fetch_all("holiday")

    if holiday_df.empty:
        print("⚠️  No data fetched or failed to connect.")
    else:
        print("✅ Fetched data sample:")
        print(holiday_df.head())
