# COMP47360_Summer_Project_Group5

## Table of Contents
- [Project Overview](#project-overview)
- [Group Members](#group-members)
- [Teamwork Documents](#teamwork-documents)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation and Setup](#installation-and-setup)
- [Usage](#usage)
- [Testing](#testing)

---

# COMP47360 Team5 Smart Restaurant Recommender 👨‍🍳🧑‍🍳

---

## Project Overview

This is the backend system for the **Smart Restaurant Busyness Recommender Web Application**. The system allows individual users or groups to receive restaurant recommendations based on multiple dynamic factors such as live busyness predictions, personal preferences, group consensus, accessibility, price level, location proximity, and cuisine match.

I designed this backend using a **modular, production-quality architecture** using Flask Blueprints and reusable utility functions. Each module (Personal, Group, Comparison, Admin) is fully separated for easier maintenance, expansion, and scalability. This will allow our team to continue adding advanced features in later sprints.

---

## Group Members

- Bingzheng Lyu
- Xiaoxia Jin
- Wan-Hua Hsieh
- Xinchi Jian
- Eli Young (**Back-End Code Lead**)
- Aadhithya Ganesh

---

## Teamwork Documents

- [Google Docs Workspace](https://drive.google.com/drive/folders/1L_c5XzWzfr3srVnpK_uKYDhjhnrImVYq?usp=drive_link)
- [GitHub Workflow Guide](Github_Workflow.md)

---

## Features

- Solo (Personal) restaurant recommendation system  
- Group-based recommendation sessions with consensus scoring  
- Full-fit score calculation for multi-user group matching  
- Heatmap backend API for city-wide busyness visualization  
- Dynamic restaurant comparison module (session-based)  
- Full Admin CRUD for restaurant management (add, delete, view)  
- Modular, scalable backend architecture (production-grade design)

---

## Technology Stack

- **Backend:** Python (Flask Framework)  
- **Database:** PostgreSQL (SQLAlchemy ORM with UUID, JSONB, ARRAY types)  
- **Frontend (handled by Adi):** React (planned)  
- **Authentication (handled by Eric):** OAuth (planned integration)  
- **APIs:** External data sources (weather, models to be integrated by Emily - Data Lead)

---

## Folder Structure (Modular Design)
```md
Backend/
│
├── run.py
├── __init__.py
├── README.md
├── APIdoc.md
│
├── app/
│   ├── __init__.py
│   ├── models.py
│
│   ├── utils/
│   │   ├── main_utils.py
│   │   ├── personal_utils.py
│   │   ├── group_utils.py
│   │   ├── comparison_utils.py
│
│   ├── authentication/
│   │   ├── authentication.py
│   │   ├── test_auth
│   │   └── README.md
│
│   ├── routes/
│   │   ├── main_routes.py
│   │   ├── personal_routes.py
│   │   ├── group_routes.py
│   │   ├── comparison_routes.py
│
├── tests/
│   ├── conftest.py
│   ├── .env.test
│
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_model_unit.py
│   │   ├── test_utils_unit.py
│   │   ├── test_group_unit.py
│   │   ├── test_main_unit.py
│   │   ├── test_comparison_unit.py
│   │   ├── test_personal_unit.py
│
│   └── integration/
│       ├── __init__.py
│       ├── README.md
│       ├── test_group_integration.py
│       ├── test_personal_integration.py
│       ├── test_main_integration.py
│       ├── test_comparison_integration.py
```
---
## Current API Endpoints (Organized by Module)

| Category       | Endpoint                                             | Method | Description                                       |
|----------------|------------------------------------------------------|--------|---------------------------------------------------|
| Main           | /healthcheck                                         | GET    | Basic health ping                                 |
|                | /                                                    | GET    | Root greeting                                     |
|                | /restaurants                                         | GET    | All restaurants with metadata and predictions     |
|                | /restaurants/<restaurant_id>                         | GET    | Full metadata for a specific restaurant           |
|                | /restaurants/<restaurant_id>/busyness                | GET    | Busyness level for a specific restaurant          |
|                | /restaurants/predictions                             | GET    | Predictions for all restaurants                   |
|                | /heatmap                                             | GET    | GeoJSON heatmap of city busyness                  |
|                | /filters/options                                     | GET    | Get all filter values                             |
|                | /restaurants/top-rated                               | GET    | Get top 25 rated restaurants with predictions     |
| Personal       | /personal/restaurant/<restaurant_id>/prediction      | GET    | Prediction near given datetime                    |
|                | /personal/recommendation                             | POST   | Personalized recommendations                      |
| Group          | /group/session/create                                | POST   | Create new group session                          |
|                | /group/session/<group_id>                            | DELETE | Delete group session                              |
|                | /group/session/<group_id>/submit_preferences         | POST   | Submit user preferences to group                  |
|                | /group/session/<group_id>/update_preferences         | PUT    | Update preferences for a user                     |
|                | /group/session/<group_id>/members                    | GET    | Get all user preferences in group                 |
|                | /group/session/<group_id>/clear                      | DELETE | Clear all preferences but keep session            |
|                | /group/session/<group_id>/results                    | GET    | Group restaurant recommendations                  |
|                | /group/session/<group_id>/join                       | POST   | Join a group session with preferences             |
|                | /group/user/<user_id>/groups                         | GET    | Get all groups a user has joined                  |
| Comparison     | /comparison/session/create                           | POST   | Create a temporary comparison session             |
|                | /comparison/session/<session_id>/add_restaurant      | POST   | Add restaurant to session                         |
|                | /comparison/session/<session_id>/remove_restaurant   | POST   | Remove restaurant from session                    |
|                | /comparison/session/<session_id>/view                | POST   | View full session with restaurant details         |
|                | /comparison/user/<user_id>/sessions                  | GET    | View all comparison sessions for a user           |
| Authentication | /authentication/signup                               | POST   | Register a new user                               |
|                | /authentication/login                                | POST   | Login with username and password                  |
|                | /authentication/profile                              | GET    | Get current user profile (JWT required)           |
|                | /authentication/profile                              | PUT    | Update current user profile (JWT required)        |

---

## Environment Variables (.env File)

| Variable                | Description                                                                 |
|-------------------------|-----------------------------------------------------------------------------|
| `DATABASE_URL`          | SQLAlchemy-compatible connection URI for the PostgreSQL database            |
| `SQLALCHEMY_DATABASE_URI` | URI used explicitly by SQLAlchemy (redundant if `DATABASE_URL` is already used) |
| `SECRET_KEY`            | Secret key used by Flask for session signing and CSRF protection            |
| `EMAIL`                 | Admin email (used for contact/deployment setup)                             |
| `PASSWORD`              | Admin password (used for database and deployment auth)                      |
| `MAIL`                  | Application email sender address (e.g. for outgoing emails via Flask-Mail)  |
| `GOOGLE_API_KEY`        | Used to access Google Maps and Places APIs for location/cuisine lookups     |
| `YELP_FUSION_API_KEY`   | API key for Yelp Fusion (restaurant metadata, ratings, etc.)                |
| `OPEN_WEATHER_API`      | API key for OpenWeatherMap (fetches current weather used in busyness model) |
| `SUPABASE_URL`          | Base URL of Supabase project (not currently used directly in backend)       |
| `SUPABASE_KEY`          | API key for Supabase project (currently unused by backend modules)          |

> Note: `SUPABASE_URL` and `SUPABASE_KEY` are not currently used in the backend.

---

## Database Schema

---

###  Table: `users`

| Column Name     | Type   | Description                   |
|-----------------|--------|-------------------------------|
| `user_id`       | UUID   | Unique identifier             |
| `name`          | String | Full name                     |
| `username`      | String | Unique username               |
| `email`         | String | Email for login               |
| `password_hash` | String | Hashed password               |
| `latitude`      | Float  | (Optional) last known lat     |
| `longitude`     | Float  | (Optional) last known lon     |

---

###  Table: `restaurants`

| Column Name                     | Type       | Description                                           |
|---------------------------------|------------|-------------------------------------------------------|
| `restaurant_id`                 | UUID       | Unique identifier                                     |
| `place_id`                      | String     | External Place ID (e.g. Google Maps)                 |
| `full_name`                     | String     | Unique name of restaurant                            |
| `cuisine_type`                 | String     | High-level cuisine category                          |
| `cuisine_keyword`             | String     | Sub-cuisine keyword                                  |
| `lat`, `lon`                    | Float      | Latitude/longitude                                    |
| `rating`                        | Float      | Average user rating                                  |
| `review_count`                 | Integer    | Number of reviews                                    |
| `price_level`                  | Integer    | 1=cheap, 2=mid, 3=expensive                          |
| `grid_id`                       | String     | Foreign key to `busyness_predictions.grid_id`        |
| `address`, `phone`, `image_url`| String     | Contact & metadata                                   |
| `inspection_id`                | String     | NYC health inspection ID                             |
| `inspection_grade`            | String     | Grade (e.g. A, B)                                    |
| `inspection_date`             | Date       | Last inspection date                                 |
| `google_name`                  | String     | Display name from Google                             |
| `restaurant_counts`            | Integer    | Count in same grid                                   |
| `geometry`                     | Geometry   | PostGIS POINT for geolocation                        |
| `lat_rounded`, `lon_rounded`   | Float      | Rounded coordinates (for heatmap grid)               |
| `has_opening_hour_data`       | Boolean    | Whether hourly opening data is available             |
| `has_popular_hour_data`       | Boolean    | Whether popular hour data is available               |
| `distance_to_*`               | Float      | Precomputed distances to benchmark locations         |


---

### Table: `groups`

| Column Name   | Type     | Description                              |
|----------------|----------|------------------------------------------|
| `group_id`     | UUID     | Unique group identifier                  |
| `group_name`   | String   | Optional session display name            |
| `created_by`   | UUID     | Creator user ID                          |
| `created_at`   | DateTime | Timestamp when session was created       |
| `members_json` | JSONB    | Dictionary of preferences per user       |

---

### Table: `busyness_predictions`

| Column Name       | Type     | Description                                |
|-------------------|----------|--------------------------------------------|
| `grid_id`         | String   | Grid location identifier                    |
| `timestamp`       | DateTime | When prediction was made                    |
| `predicted_level` | Integer  | Busyness score (0–2)                        |

---

### Table: `group_fit_scores`

| Column Name    | Type     | Description                                     |
|----------------|----------|-------------------------------------------------|
| `score_id`     | UUID     | Unique fit score ID                             |
| `group_id`     | UUID     | Foreign key to `groups.group_id`               |
| `restaurant_id`| UUID     | Foreign key to `restaurants.restaurant_id`     |
| `timestamp`    | DateTime | When score was computed                         |
| `fit_score`    | Float    | Normalized score (0.0–1.0)                       |
| `fit_breakdown`| JSONB    | Optional score component breakdown              |

---

### Table: `personal_fit_scores`

| Column Name     | Type     | Description                                    |
|------------------|----------|------------------------------------------------|
| `score_id`       | UUID     | Unique score ID                                |
| `user_id`        | UUID     | Foreign key to `users.user_id`                |
| `restaurant_id`  | UUID     | Foreign key to `restaurants.restaurant_id`    |
| `timestamp`      | DateTime | When score was computed                        |
| `fit_score`      | Float    | Score between 0 and 1                          |
| `fits_breakdown` | JSON     | Feature-wise score breakdown                   |

---

### Table: `comparison_sessions`

| Column Name        | Type     | Description                                     |
|--------------------|----------|-------------------------------------------------|
| `session_id`       | UUID     | Unique session ID                               |
| `created_by`       | UUID     | Unique ID for user                              |
| `created_at`       | DateTime | When session was created                        |
| `expires_at`       | DateTime | When session expires                            |
| `restaurants_json` | JSONB    | List of compared restaurants                    |

---

### Table: `location_mapping`

| Column Name   | Type     | Description                       |
|---------------|----------|-----------------------------------|
| `main_location` | String | Region label                      |
| `geometry`      | Geometry| PostGIS POLYGON for mapping zone  |

---

### Table: `grid_info`

| Column Name        | Type     | Description                           |
|--------------------|----------|---------------------------------------|
| `grid_id`          | String   | Unique grid ID                        |
| `lat`, `lon`       | Float    | Center coordinates                    |
| `geometry`         | Geometry| PostGIS POLYGON shape of the grid     |
| `restaurant_count` | Integer  | Number of restaurants in the grid     |
| `population`       | Integer  | (Optional) population in the area     |

---

### Table: `holiday`

| Column Name   | Type | Description                |
|---------------|------|----------------------------|
| `holiday_date`| Date | Public/national holiday    |

---

### Table: `restaurant_popular_hour`

| Column Name | Type     | Description                                     |
|--------------|----------|-------------------------------------------------|
| `place_id`   | String   | Google place ID                                 |
| `day`        | String   | Day of week                                     |
| `hour_0`...`hour_23` | Integer | Popularity score for each hour (0–23)   |

---

### Table: `restaurant_opening_hour`

| Column Name | Type     | Description                                     |
|--------------|----------|-------------------------------------------------|
| `place_id`   | String   | Google place ID                                 |
| `day`        | String   | Day of week                                     |
| `hour_0`...`hour_23` | Boolean | Open/closed flag for each hour         |

---

### Table: `latest_grid_busyness`

| Column Name       | Type     | Description                                  |
|--------------------|----------|----------------------------------------------|
| `grid_id`          | String   | Grid ID (one row per grid)                   |
| `predicted_level`  | Integer  | Current prediction (e.g., 0=Low, 2=High)     |
| `timestamp`        | DateTime | When it was last updated                     |
| `geometry`         | Geometry | Optional polygon for frontend overlays       |

---

## Testing

The backend test suite is written using **pytest**. Tests are modularized to align with backend architecture (routes, utils, models).

### Current Test Coverage

Test scaffolding and logic is included for both **unit** and **integration** testing:

#### Unit Tests (`tests/unit/`)

| Test File                   | Description                                                                 |
|-----------------------------|-----------------------------------------------------------------------------|
| `test_model_unit.py`        | Verifies model structure, relationships, data types, default values         |
| `test_utils_unit.py`        | Tests scoring helpers (distance calc, normalization, breakdown logic)       |
| `test_personal_unit.py`     | Isolated tests for solo recommendation logic and score calculations         |
| `test_group_unit.py`        | Unit tests for Fit Score aggregation and user preference handling           |
| `test_main_unit.py`         | Validates filtering, heatmap generation, and main route formatting          |
| `test_comparison_unit.py`   | Simulates add/remove/view of comparison sessions (mocked DB)                |
| `__init__.py`               | Unit test module initializer                                                 |

#### Integration Tests (`tests/integration/`)

| Test File                        | Description                                                                      |
|----------------------------------|----------------------------------------------------------------------------------|
| `test_personal_integration.py`  | Full POST flow for personal recommendations using real database entries         |
| `test_group_integration.py`     | Creates group session, submits user preferences, validates Fit Score ordering   |
| `test_main_integration.py`      | GET routes for restaurants, filters, busyness predictions, and heatmap          |
| `test_comparison_integration.py`| End-to-end flow for creating a comparison session and viewing restaurant data    |
| `readme`                         | Notes on integration test setup or DB state assumptions                         |
| `__init__.py`                    | Integration test module initializer                                              |

#### Shared Test Setup

| Test File             | Description                                                                      |
|-----------------------|----------------------------------------------------------------------------------|
| `conftest.py`         | Pytest fixtures for Flask test client, mock app context, test DB initialization |
| `.env.test`           | Test-specific environment variables (e.g., `DATABASE_URL`)                      |

---

### Example Test Areas

- **Personal**: Ranking of solo restaurant recommendations, prediction retrieval, distance penalties  
- **Group**: Consensus-based Fit Score evaluation from diverse user preferences  
- **Comparison**: Validation of session-based comparisons, expiry logic, duplicate handling  
- **Main**: Route response structure, filter options, busyness overlay results  
- **Models**: Field correctness, unique constraints, foreign keys, JSONB structure  
- **Utils**: Logic for location scoring, cuisine matching, time filtering, grid calculations  
- **Integration**: Combined route-to-model verification under real API usage

---

Coverage aligns with production modules and supports **Sprint 5 demo readiness** and **deployment validation**.


### How to Run Tests

This backend powers the **COMP47360 Summer Project – Restaurant Busyness Predictor and Recommendation System**, using Flask, SQLAlchemy, and PostgreSQL. Follow these steps to run it locally using a virtual environment — **everything is in this one markdown cell**.

### Step-by-Step Setup

#### 1. Clone and move into the project folder
```bash
cd COMP47360_Summer_Project_Group5/app/Backend
ls # Check requirements.txt in this folder
```

#### 2. Create and activate your Python virtual environment
- Install by Python3
```bash
python3 -m venv venv
source venv/bin/activate
```
- Install by conda
```bash
conda env list # Check exited virtual env
conda create --name comp47360 python=3.11
conda activate comp47360
```

#### 3. Install required Python dependencies
```bash
pip install -r requirements.txt
```

#### 4. Log into PostgreSQL as the default superuser
Before login PostgreSQL, check if you install PostgreSQL and PostGIS extension in your system.
- **MacOS system**: By using Homebrew to install PostgreSQL and PostGIS, type`brew install postgresql@14 postgis`
- **Window system**: 
    1. Download PostgreSQL from here [PostgreSQL Windows installers](https://www.postgresql.org/download/windows/);
    2. After installation, check the box to run StackBuilder at the "Finish" screen:
        - Select the version of PostgreSQL you just installed (e.g., PostgreSQL 14 x64).
        - From the package list: Go to "Spatial Extensions", select "PostGIS" (usually includes postgis, postgis_topology, and sometimes postgis_sfcgal)
        - Click Next and follow the prompts to download and install PostGIS.
- **Linux system**: Type these command line below:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib postgis postgresql-14-postgis-3
```

Start PostgreSQL after you install them:
```bash
psql -U postgres
```

#### 5. Create a new clean test database
```bash
DROP DATABASE IF EXISTS restaurant_test_db;
CREATE DATABASE restaurant_test_db;
\q
```

#### 6. Connect to the new test database directly
```bash
psql -U postgres -d restaurant_test_db
```

#### 7. Enable the PostGIS extension
```bash
CREATE EXTENSION postgis;
\dx  -- (optional) verify that PostGIS is listed
\q
```

#### 8. Run the full test suite
```bash
cd app/Backend
pytest
```

**Maintained by Eli Young — Backend Code Lead**