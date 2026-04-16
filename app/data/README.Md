# 📂 Data Directory Overview

This directory contains all datasets, intermediate outputs, and documentation related to the **data preprocessing and model development pipeline** for the **Smart Restaurant Busyness Recommender** project.

It covers the full workflow from **raw data collection** to **model development and evaluation**, ensuring transparency and reproducibility.

## 🔑 Key Contents

| Path                | Purpose                                                                                      |
|----------------------|----------------------------------------------------------------------------------------------|
| `data_preparation/`  | Raw datasets and intermediate outputs, partially cleaned and organized, ready to be used for model development   |
| `model_development/` | Jupyter Notebooks and artifacts covering data preparation, modeling, evaluation, and prediction |
| `scripts/`           | Utility scripts for future busyness prediction, designed for direct integration with the backend; includes functions for fetching real-time data, loading data from the database, creating features for future timestamps, and returning prediction results                                       |
| `environment.yml`    | Conda environment configuration for reproducibility                                            |
| `example.env`        | Example environment variables required to run the project                                      |

---
# Directory Structure and Purpose
## 📂 `data_preparation/`

```plaintext
data_preparation/
├── bike_subway_grid_overlap/     
│   ├── bike_subway_grid_overlap.ipynb
│   ├── multiple_station_bike_grids.csv
├── citi_bike/
│   ├── bike_station_df.csv
│   ├── citi_bike.ipynb
├── event_data/
│   ├── event_data.ipynb
├── holiday_module/Holiday/
│   ├── combined_ny_holidays.csv
│   ├── holiday.ipynb
│   ├── new-york.ics
├── hourly_weather/
│   ├── hourly_weather_data.ipynb
│   ├── hourly_weather_data_20240401_20250331.csv
├── inspection/
│   ├── Inspection_*.csv (multiple files)
│   ├── inspection_cleaning_matching.ipynb
├── manhattan_grid/
│   ├── manhattan_grid.csv
│   ├── taxi_location_grid_mapping.csv
│   ├── taxi_zones.csv
│   ├── manhattan_grid.ipynb
├── mta_subway/
│   ├── mta_subway.ipynb
│   ├── mta_subway_20240101_20250430.csv
├── population/
│   ├── census_data_2020.csv
│   ├── population.ipynb
├── prepared_outputs/
│   ├── grid_info.csv
│   ├── holiday_df.csv
│   ├── location_df.csv
│   ├── restaurant_info.csv
├── restaurant_data_fetching/
│   ├── restaurant_info.csv
│   ├── yelp_fusion.ipynb
│   ├── google_place.ipynb
│   ├── ... (other intermediate files)
├── wheelchair_accessibility/Wheelchair_Friendly/
│   ├── manhattan_wheelchair_friendly_restaurants.csv
│   ├── wheelchair_friendly_scraper.ipynb
├── yellow_taxi/
│   ├── yellow_taxi.ipynb
```

(Other intermediate files omitted for brevity)

### 📑 `data_preparation/` Subfolder Purposes

| Folder                               | Purpose / Description                                                   |
|--------------------------------------|---------------------------------------------------------------------------|
| `bike_subway_grid_overlap/`          | Analyze the density of CitiBike and subway stations within each grid cell to understand data distribution. |
| `citi_bike/`                         | Analyze CitiBike station usage volume as an indicator of local busyness. |
| `event_data/`                        | Collect and process event times and locations, converting them into spatial features to reflect potential crowd fluctuations. |
| `holiday_module/Holiday/`            | Public holidays in NYC, used as temporal features impacting abnormal busyness. |
| `hourly_weather/`                    | Hourly weather data, used as environmental factors correlated with busyness. |
| `inspection/`                        | Official restaurant inspection records, used for restaurant list generation and attribute enrichment. |
| `manhattan_grid/`                    | Grid definitions and mappings to NYC geography and transportation zones, serving as spatial analysis units. |
| `mta_subway/`                        | Subway station usage data, used as an indicator of busyness levels. |
| `population/`                        | Census population data by grid, providing baseline context for potential busyness. |
| `prepared_outputs/`                  | Cleaned and merged datasets stored in the database, prepared for model training. |
| `restaurant_data_fetching/`          | Google/Yelp restaurant metadata, popular times, and opening hours, used to enrich restaurant attributes and popularity estimation. |
| `wheelchair_accessibility/`          | Locations of wheelchair-accessible facilities, used as supplementary restaurant attributes. |
| `yellow_taxi/`                       | Yellow Taxi hotspot data, used as an indicator of local busyness. |

---

## 📁 `model_development/`

```plaintext
model_development/
├── 00_prepare_model_dataset.ipynb
├── 01_initial_busyness_score_design.ipynb
├── 02_model_comparison_and_selection.ipynb
├── 03_final_score_refinement_and_model_evaluation.ipynb
├── 04_generate_future_prediction_features.ipynb
├── 10_reprocess_dataset_and_eda.ipynb
├── 11_score_evaluation.ipynb
├── 12_model_evaluation.ipynb
├── busyness_score_restaurant.ipynb
├── lgbm_model.pkl
├── lgbm_model_v2.pkl
├── lgbm_model_v3.pkl
├── optuna_trial_log.txt
```

### 📑 `model_development/` File Purposes

| File                                           | Purpose / Description                                                |
|------------------------------------------------|------------------------------------------------------------------------|
| `00_prepare_model_dataset.ipynb`               | Prepare datasets for model training.                                   |
| `01_initial_busyness_score_design.ipynb`       | Design and evaluate initial baseline busyness score.                   |
| `02_model_comparison_and_selection.ipynb`      | Compare candidate models and select the best-performing one.            |
| `03_final_score_refinement_and_model_evaluation.ipynb` | Refine final score and conduct model evaluation.                  |
| `04_generate_future_prediction_features.ipynb` | Generate future timestamps' features for prediction.                   |
| `10_reprocess_dataset_and_eda.ipynb`           | Reprocess datasets and conduct additional exploratory analysis.        |
| `11_score_evaluation.ipynb`                    | Evaluate the distribution and characteristics of the busyness score.    |
| `12_model_evaluation.ipynb`                    | Final model evaluation and validation.                                  |
| `busyness_score_restaurant.ipynb`              | Integrate restaurant data with busyness scores for analysis.            |
| `lgbm_model.pkl`                               | Final trained LightGBM model (version 1).                               |
| `lgbm_model_v2.pkl`                            | Final trained LightGBM model (version 2).                               |
| `lgbm_model_v3.pkl`                            | Final trained LightGBM model (version 3).                               |
| `optuna_trial_log.txt`                         | Hyperparameter tuning logs for reproducibility.                         |

---
## 📁 `script/`

```plaintext
script/
├── db/
│   └── supabase_client.py
├── fetchers/
│   ├── event_fetcher.py
│   └── weather_fetcher.py
├── model/
│   ├── lgbm_model_v3.pkl
│   └── run_prediction.py
```

### 📑 `script/` File Purposes

| Path / File                  | Purpose / Description                                                      |
|-------------------------------|-----------------------------------------------------------------------------|
| `db/supabase_client.py`       | Utilities to query Supabase database for real-time data.                    |
| `fetchers/event_fetcher.py`   | Fetch and preprocess external event data for prediction input.              |
| `fetchers/weather_fetcher.py` | Fetch and preprocess weather data for prediction input.                     |
| `model/lgbm_model_v3.pkl`     | Trained LightGBM model version 3 for busyness prediction (current version). |
| `model/run_prediction.py`     | Main script to run prediction pipeline, including feature creation and inference. |

---

## 🗂 Data Source for Database Tables (For Reference Only)

The following datasets were used to create the existing database tables.  
No further action is required from the backend side.

| Table Name               | Source CSV Location                                     |
|---------------------------|--------------------------------------------------------|
| `location_mapping`        | `prepared_outputs/location_df.csv`                     |
| `grid_info`               | `prepared_outputs/grid_info.csv`                       |
| `holiday`                 | `prepared_outputs/holiday_df.csv`                      |
| `restaurant_info`         | `prepared_outputs/restaurant_info.csv`         |
| `restaurant_popular_hour` | `restaurant_data_fetching/restaurant_popular_hour.csv` |

---

# 🔮 How to Predict Busyness with the Model

## 1️⃣ Set Up Environment
1. Navigate to the `data/` directory.
2. Create the Conda environment:
    ```bash
    conda env create -f environment.yml
    ```
3. Activate the environment:
    ```bash
    conda activate spg5
    ```

---

## 2️⃣ Set Up API Keys  
1. Copy `example.env` and rename it to `.env`.  
2. Fill in your API keys directly in `.env`. (No quotation marks needed.)  

**Required APIs:**  
- **Google Maps Places API**  
    - [API Key Setup](https://developers.google.com/maps/documentation/places/web-service/get-api-key)  
- **OpenWeather One Call API 3.0**  
    - [API Key Setup](https://openweathermap.org/api)

**⚠️ Do not commit your `.env` file to GitHub.**

---

## 3️⃣ Run Prediction

You can obtain predicted busyness levels for specific future timestamps via either:
- A **command-line script**
- **Importing and calling the predictor class directly**

### Option 1: Run via Script
Predict busyness levels for **3 days later**:
```bash
python3 data/script/run_prediction.py
```

### Option 2: Import and Use the Predictor Programmatically
```python
import datetime
from run_prediction import BusynessPredictor

# Target datetime (e.g., 3 days later)
target_dt = datetime.datetime.now() + datetime.timedelta(days=3)

# Run prediction
print(f"🔍 Predicting busyness at: {target_dt}")
predictor = BusynessPredictor(target_datetime=target_dt)
result = predictor.predict()

# Show prediction sample
print("✅ Sample prediction result:")
print(result.head())
```