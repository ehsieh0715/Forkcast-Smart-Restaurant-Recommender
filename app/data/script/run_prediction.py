import datetime
import os
from zoneinfo import ZoneInfo

import joblib
import pandas as pd
from dotenv import load_dotenv
from fetchers.event_fetcher import EventDataFetcher
from fetchers.weather_fetcher import WeatherDataFetcher
from shapely.wkt import dumps
from supabase_utils.supabase_client import SupabaseClient

# Load environment variables from .env file
load_dotenv()

# 1. Find the directory this script lives in
script_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Join it with the child "model" folder and your pickle filename
model_path = os.path.join(script_dir, "model", "lgbm_model_v3.pkl")


class BusynessPredictor:
    """
    Predicts hourly busyness levels for spatial grid cells across Manhattan.
    Includes weather, event, time, spatial features. Outputs include geometry polygons.
    """

    def __init__(self, target_datetime: datetime.datetime):
        self.target_datetime = pd.to_datetime(target_datetime).round("h")
        self.supabase = SupabaseClient()

    def fetch_event_data(self):
        fetcher = EventDataFetcher(target_datetime=self.target_datetime)
        return fetcher.get_hourly_grid_event()

    def fetch_weather_data(self):
        fetcher = WeatherDataFetcher(target_datetime=self.target_datetime)
        return fetcher.get_forecast()

    def _construct_features(self):
        grid_info = self.supabase.fetch_all("grid_info")
        holiday_df = self.supabase.fetch_all("holiday")
        weather_df = self.fetch_weather_data()
        event_df = self.fetch_event_data()
        holiday_df["holiday_date"] = pd.to_datetime(holiday_df["holiday_date"])
        feature_df = grid_info.merge(weather_df, how="cross").merge(
            event_df, how="left", on="grid_id"
        )
        feature_df["datetime"] = self.target_datetime
        feature_df["event_count"] = feature_df["event_count"].fillna(0)

        # Time-based features
        feature_df["grid_id"] = feature_df["grid_id"].astype("category")
        feature_df["month"] = feature_df["datetime"].dt.month.astype("category")
        feature_df["weekofyear"] = (
            feature_df["datetime"].dt.isocalendar().week.astype("category")
        )
        feature_df["dayofweek"] = feature_df["datetime"].dt.dayofweek.astype("category")
        feature_df["day"] = feature_df["datetime"].dt.day.astype("category")
        feature_df["hour"] = feature_df["datetime"].dt.hour.astype("category")

        is_holiday = (
            self.target_datetime.normalize() in holiday_df["holiday_date"].values
        )
        feature_df["is_holiday"] = is_holiday
        feature_df["is_holiday"] = feature_df["is_holiday"].astype("category")
        feature_df["is_weekend"] = (feature_df["dayofweek"].astype(int) >= 5).astype(
            "category"
        )

        columns = [
            "month",
            "weekofyear",
            "dayofweek",
            "is_weekend",
            "day",
            "hour",
            "is_holiday",
            "temp_c",
            "dew_c",
            "wind_speed_knot",
            "precip_mm",
            "grid_id",
            "restaurant_count",
            "population",
            "lat",
            "lon",
            "event_count",
            "geometry",
        ]
        return feature_df[columns]

    def predict(self):
        feature_df = self._construct_features()
        model = joblib.load(model_path)
        preds = model.predict(feature_df.drop(columns="geometry"))

        result_df = feature_df.copy()
        result_df["predicted_level"] = preds + 1
        result_df["timestamp"] = self.target_datetime
        return result_df[["grid_id", "predicted_level", "timestamp", "geometry"]]


if __name__ == "__main__":
    now_ny = (
        pd.Timestamp.now(tz=ZoneInfo("America/New_York")).round("h").tz_localize(None)
    )
    end_ny = now_ny + pd.Timedelta(days=7)

    future_hours = pd.date_range(start=now_ny, end=end_ny, freq="1h")

    for target_dt in future_hours:
        predictor = BusynessPredictor(target_datetime=target_dt)
        print(predictor.target_datetime)
        result = predictor.predict()

        # Convert geometry to WKT string and overwrite 'geometry' column for DB storage
        upload_df = result.copy()
        upload_df["timestamp"] = upload_df["timestamp"].dt.strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        upload_df["geometry"] = upload_df["geometry"].apply(dumps)
        print("🔄 Inserting into busyness_predictions...")
        predictor.supabase.insert_all(
            "busyness_predictions",
            upload_df[["grid_id", "predicted_level", "timestamp", "geometry"]],
            upsert=True,
        )
