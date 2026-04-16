import datetime
import json
import os
from zoneinfo import ZoneInfo

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()


class WeatherDataFetcher:
    """
    Fetches weather forecast data for Manhattan using OpenWeather One Call API 3.0.

    Supports current, hourly (next 48 hours), and daily (up to 7 days) forecasts.
    """

    def __init__(self, target_datetime: datetime):
        """
        Initializes the WeatherDataFetcher with target time and setup.

        Args:
            target_datetime (datetime): Target time for weather prediction (rounded to the nearest hour). NY time
        """
        dt_ny = pd.to_datetime(target_datetime).tz_localize(
            ZoneInfo("America/New_York")
        )
        self.target_datetime = (
            dt_ny.astimezone(ZoneInfo("Europe/Dublin")).tz_localize(None).round("h")
        )
        self.current_datetime = self.current_datetime = pd.to_datetime(
            datetime.datetime.now()
        ).round("h")
        self.api_key = os.getenv("OPEN_WEATHER_API")
        self.lat = 40.77898  # Latitude for Manhattan
        self.lon = -73.96925  # Longitude for Manhattan

    def get_forecast(self):
        """
        Main function to fetch weather forecast based on the target datetime.

        Returns:
            pd.DataFrame or None: Weather data with selected fields or None if out of valid range.
        """
        if not self._is_valid_range():
            return None
        raw_data = self._fetch_weather_data()
        if self._is_within_47h():
            return self._parse_hourly_weather(raw_data)
        else:
            return self._parse_daily_weather(raw_data)

    def _is_valid_range(self):
        """
        Validates that the target datetime is within the forecastable range (0–7 days ahead).

        Returns:
            bool: True if valid, False otherwise.
        """
        if (self.target_datetime - self.current_datetime) > datetime.timedelta(days=8):
            print("❗ Can only predict weather up to 7 days in advance.")
            return False
        elif self.target_datetime < self.current_datetime:
            print("❗ Cannot predict weather in the past.")
            return False
        return True

    def _is_within_47h(self):
        """Checks if the target datetime is within 47 hours."""
        return (self.target_datetime - self.current_datetime) < datetime.timedelta(
            hours=47
        )

    def _fetch_weather_data(self):
        """
        Fetches raw weather data from OpenWeather API or local cache.
        Returns:
            dict: Parsed JSON response from the API.
        """
        current_dt_str = self.current_datetime.strftime("%Y%m%d_%H%M")
        filename = f"weather_{current_dt_str}.json"

        # If file exists, load from file
        if os.path.exists(filename):
            print(f"📂 Loading cached weather data from {filename}")
            with open(filename, "r") as f:
                return json.load(f)

        # Otherwise, fetch from API
        print("🌐 Fetching weather data from API...")
        url = (
            f"https://api.openweathermap.org/data/3.0/onecall?"
            f"lat={self.lat}&lon={self.lon}&exclude=minutely,alerts&units=metric&appid={self.api_key}"
        )
        response = requests.get(url)
        data = response.json()
        # Save to file
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)

        return data

    def _parse_hourly_weather(self, data):
        """
        Parses hourly weather forecast.

        Args:
            data (dict): Raw weather API data.

        Returns:
            pd.DataFrame: Parsed hourly forecast matching target datetime.
        """
        df = pd.DataFrame(data["hourly"])
        df["datetime"] = pd.to_datetime(df["dt"], unit="s") + pd.to_timedelta(
            1, unit="h"
        )
        df = df[df["datetime"] == self.target_datetime].copy()
        df["temp_c"] = df["temp"]
        return self._postprocess_weather(df)

    def _parse_daily_weather(self, data):
        """
        Parses daily weather forecast.

        Args:
            data (dict): Raw weather API data.

        Returns:
            pd.DataFrame: Daily weather forecast matching target date.
        """
        df = pd.DataFrame(data["daily"])
        df["datetime"] = pd.to_datetime(df["dt"], unit="s") + pd.to_timedelta(
            1, unit="h"
        )
        df["temp_c"] = df["temp"].apply(lambda x: x["day"])
        df["precip_mm"] = df.get("rain", 0).astype(float).fillna(0) / 24
        df = df[df["datetime"].dt.date == self.target_datetime.date()].copy()
        return self._postprocess_weather(df)

    def _postprocess_weather(self, df):
        """
        Standardizes and selects final weather features.

        Args:
            df (pd.DataFrame): Raw weather data.

        Returns:
            pd.DataFrame: Cleaned weather data with relevant features.
        """
        df["wind_speed_knot"] = df["wind_speed"] * 1.94384
        df["precip_mm"] = df.apply(
            lambda row: (
                row["rain"]["1h"]
                if isinstance(row.get("rain"), dict) and "1h" in row["rain"]
                else row.get("precip_mm", 0)
            ),
            axis=1,
        )
        df = df.rename(columns={"dew_point": "dew_c"})
        return df[["temp_c", "dew_c", "wind_speed_knot", "precip_mm"]].reset_index(
            drop=True
        )


if __name__ == "__main__":
    now_ireland = pd.Timestamp.now(tz=ZoneInfo("Europe/Dublin")).round("h")
    dt = now_ireland.to_pydatetime()
    now_dt = dt.astimezone(ZoneInfo("America/New_York")).replace(tzinfo=None)

    # Test Case 1: Current datetime
    print("Test Case 1: Current datetime:", now_dt)
    fetcher = WeatherDataFetcher(target_datetime=now_dt)
    result = fetcher.get_forecast()
    print(result)

    # Test Case 2: Datetime in the past
    past_dt = now_dt - datetime.timedelta(hours=1)
    print("Test Case 2: Datetime in the past:", past_dt)
    fetcher = WeatherDataFetcher(target_datetime=past_dt)
    result = fetcher.get_forecast()
    print(result)

    # Test Case 3: Datetime after 7 days
    future_dt = now_dt + datetime.timedelta(days=9)
    print("Test Case 3: Datetime after 7 days:", future_dt)
    fetcher = WeatherDataFetcher(target_datetime=future_dt)
    result = fetcher.get_forecast()
    print(result)
