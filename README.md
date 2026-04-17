# Forkcast - Smart Restaurant Recommender 👨‍🍳🧑‍🍳

Web-based system for predicting restaurant busyness in Manhattan using data analytics and machine learning, integrating real-time data, user preferences, and contextual features.

![Role](https://img.shields.io/badge/Role-Data%20Lead-green)
![Stack](https://img.shields.io/badge/Stack-React%20%7C%20Flask%20%7C%20PostgreSQL-orange)
![Status](https://img.shields.io/badge/Status-Reproducible%20%7C%20Deployment%20Paused-blue)

## 🔗 Original Project
This repository is a personal version of a collaborative summer project.

Original repository: [Forkcast-Smart-Restaurant-Recommender](https://github.com/Justetete/Forkcast-Smart-Restaurant-Recommender)

Shared with permission from the original authors.

## 🚀 My Contribution
**Role: Data Lead**

- Defined problem formulation and overall data strategy  
- Led data sourcing, cleaning, and feature engineering pipeline  
- Developed and optimized machine learning models for busyness prediction  
- Designed product features based on data insights  
- Collaborated with frontend and backend teams on integration and UX  

## 📊 Key Results
- Built a predictive system for real-time and future restaurant busyness  
- Integrated multiple data sources (weather, location, user preferences)  
- Enabled both individual and group-based dining recommendations  
- Supported forecasting up to 5 days ahead  


## 🌟 Project Overview
Forkcast is a web-based application designed to help users make smarter dining decisions in Manhattan, NYC.

It predicts real-time and future restaurant busyness levels by combining live data analytics, machine learning models, and contextual factors such as accessibility, cuisine type, and weather conditions.

Deployment is currently paused to reduce hosting costs. The full source code and setup instructions are available in this repository.

## 📋 Table of Contents
- [Features](#-features)
- [Technology Stack](#️-technology-stack)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
- [Testing](#-testing)
- [Project Structure](#️-project-structure)
- [Teamwork Documents](#-teamwork-documents)
- [Group Members](#-group-members)
- [Contributing](#-contributing)
- [License](#-license)


## ✨ Features
- 📊 Busyness prediction (real-time + future)
- 👥 Group dining coordination
- 📍 Restaurant comparison dashboard


## ⚙️ Technology Stack
- **Frontend:** React, JavaScript, Tailwind CSS, Vite  
- **Backend:** Flask (Python)  
- **Database:** PostgreSQL  
- **Tools:** Docker, Git, Postman, Figma  

## 🚀 Getting Started

### Prerequisites
- Docker: [Get Docker](https://docs.docker.com/get-started/get-docker/)

### Installation
```bash
git clone https://github.com/Justetete/COMP47360_Summer_Project_Group5.git
cd COMP47360_Summer_Project_Group5/app
docker-compose build --no-cache
```

### Configuration
1. Create a `.env` file in `/app`:  
    ```env
    GOOGLE_API_KEY=
    YELP_FUSION_API_KEY=
    OPEN_WEATHER_API=
    MAIL=
    PASSWORD=
    SUPABASE_URL=
    SUPABASE_KEY=
    DATABASE_URL=
    ```
2. Run
    ```bash
    docker-compose up
    # or
    docker-compose up -d
    ```
3. Access: `http://localhost`

## 🧬 Testing

**Backend**
```bash
pip install -r app/Backend/requirements.txt
pytest -v
```
**Frontend**
```bash
npm test
```

More details:
- [Unit Tests](app/Backend/tests/unit/README.md)
- [Integration Tests](app/Backend/tests/integration/README.md)


## 🏗️ Project Structure
<details>
  <summary>Project Structure</summary>
  
  ```md
  Smart Restaurant Recommender repo/dev branch/
  ├── app/
  │	  ├── Frontend/        # See the README.md inside the Frontend folder for details
  │	  ├── Backend/
  │	  │	  ├── app/
  │   │   │   ├── __init__.py               # Flask app initialization and Blueprint registration
  │   │   │   ├── models.py                 # All database models (SQLAlchemy ORM)
  │   │   │   ├── routes/                   # Blueprinted route handlers by module
  │   │   │   │   ├── main_routes.py        # Admin routes, restaurant CRUD, heatmap, listing
  │   │   │   │   ├── personal_routes.py    # Solo user recommendations (personal)
  │   │   │   │   ├── group_routes.py       # Group session handling & group fit score
  │   │   │   │   ├── authentication.py
  │   │   │   │   └── comparison_routes.py  # Comparison module with session-based comparisons
  │   │   │   ├── utils/                    # Reusable scoring & helper functions
  │   │   │   │   ├── main_utils.py
  │   │   │   │   ├── personal_utils.py
  │   │   │   │   ├── group_utils.py
  │   │   │   │   ├── comparison_utils.py
  │   │   │   │   └── authentication_utils.py
  │   │   │   └── tests/    # Scaffolded test cases per module (ready for Sprint 5)
  │   │   │       ├── conftest.py
  │   │   │       ├── integration/ 
  │   │   │       │   ├── README.md
  │   │   │       │   ├── __init__.py
  │   │   │       │   ├── test_comparison_integration.py
  │   │   │       │   ├── test_group_integration.py   
  │   │   │       │   ├── test_main_integration.py 
  │   │   │       │   └── test_personal_integration.py 
  │   │   │       └── unit/
  │   │   │           ├── __init__.py
  │   │   │           ├── README.md
  │   │   │           ├── test_auth.py
  │   │   │           ├── test_comparison_unit.py   
  │   │   │           ├── test_group_unit.py 
  │   │   │           ├── test_model_unit.py 
  │   │   │           ├── test_personal_unit.py
  │   │   │           └── test_utils_unit.py
  │   │   ├── __init__.py
  │   │   ├── .gitignore                    # Stuff for github to ignore
  │   │   ├── APIdoc.md                     # API documentation
  │   │   ├── Dockerfile                    # Flask image file
  │   │   ├── requirements.txt              # Python dependency list
  │   │   ├── run.py                        # Application entry point
  │   │   └── README.md                     # Backend documentation
  │   │
  │   ├── data/
  │   │   ├── data_preparation/                     # Data preprocessing modules
  │   │   │   ├── yellow_taxi                       # Yellow taxi trip data and processing
  │   │   │   ├── citi_bike                         # Citi Bike trip data and processing 
  │   │   │   ├── mta_subway                        # Subway ridership data processing
  │   │   │   ├── manhattan_grid                    # Grid generation and taxi zone mapping
  │   │   │   ├── bike_subway_grid_overlap          # Matching between bike stations and grid zones
  │   │   │   ├── inspection                        # Restaurant inspection data cleaning and integration
  │   │   │   ├── restaurant_data_fetching          # Google and Yelp restaurant metadata fetching and cleaning
  │   │   │   ├── wheelchair_accessibility          # Wheelchair-friendly restaurant scraping
  │   │   │   ├── event_data                        # NYC event data collection and processing
  │   │   │   ├── holiday_module                    # Public holiday data processing
  │   │   │   ├── hourly_weather                    # Hourly weather data processing
  │   │   │   ├── population                        # Population data processing by census block
  │   │   │   └── prepared_outputs                  # Final datasets used by backend APIs
  │   │   ├── model_development/                    # Model training, evaluation, and artifacts
  │   │   │   ├── 00_prepare_model_dataset.ipynb     # Dataset assembly for model training
  │   │   │   ├── 01_initial_busyness_score_design.ipynb  # Initial model design and feature exploration
  │   │   │   ├── 02_model_comparison_and_selection.ipynb # Cross-model comparison and selection
  │   │   │   ├── 03_final_score_refinement_and_model_evaluation.ipynb # Final tuning and validation
  │   │   │   ├── 04_generate_future_prediction_features.ipynb   # Generate feature datasets for predicting future restaurant busyness
  │   │   │   ├── busyness_score_restaurant.ipynb    # Predict restaurant-level busyness score
  │   │   │   ├── lgbm_model.pkl                     # Trained LGBM model (baseline)
  │   │   │   ├── lgbm_model_v2.pkl                  # Refined LGBM model (with tuning)
  │   │   │   │ # Intermediate datasets used during model development 
  │   │   │   ├── combined_integrated_df.pkl                  # Full integrated dataset before modeling
  │   │   │   ├── combined_with_all_columns_and_busyness_level.pkl  # Full columns version 
  │   │   │   ├── combined_light_with_busyness_level.pkl      # Lightweight version with features and target busyness_level
  │   │   │   └── optuna_trial_log.txt              # Log of Optuna hyperparameter search
  │   │   │   # ⚠️ Pkl files are not stored in GitHub due to file size. Available in shared Google Drive.
  │   │   ├── script/                               # Scripts for automated data fetching and inference
  │   │   │   ├── db                                # Supabase database client helper
  │   │   │   ├── fetchers                          # Event data API fetcher and Weather data API fetcher
  │   │   │   └── model                             # Model used for live prediction
  │   │   ├── environment.yml                       # Conda environment definition file
  │   │   ├── example.env                           # Template of environment variables
  │   │	  └── README.md                             # Documentation for the data module
  │	  └── nginx/
  │       ├── default.conf
  │       └── Dockerfile
  ├── documents/
  │   ├── tests/
  │   │   ├── Unit_testing.md
  │   │   └── Integration_testing.md
  │   ├── Github_Workflow.md
  │   └── System Structure.png
  │
  ├── .github/workflows/
  │   ├── code-quality.yml.                         # Github action workflow to check code quality of project
  │   └── Deploy-frontend.yml                       # Github action workflow to automatically deploy server on UCD server
  │
  ├── .gitignore                                    # Ignored files for repo
  ├── .dockerignore                                 # Ignored docker files for creating docker images
  ├── LICENSE
  └── README.md
  ```
</details>


## 📑 Teamwork documents
- [Google docs](https://drive.google.com/drive/folders/1L_c5XzWzfr3srVnpK_uKYDhjhnrImVYq?usp=drive_link)
- [Github Workflow](documents/Github_Workflow.md)
- [Data team document](app/data/README.md)
- [Backend team document](app/Backend/README.md)
- [Frontend team document](app/Frontend/README.md)
- [API document](app/Backend/APIdoc.md)

## 👩‍💻🧑‍💻 Group Members
- Bingzheng Lyu
- Xiaoxia Jin
- Wan-Hua Hsieh
- Xinchi Jian
- Eli Young
- Aadhithya Ganesh

## 🤝 Contributing
We welcome contributions! 🎉 If you'd like to contribute, please follow these steps:

1. Fork the repository.

2. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. Commit your changes:
   ```bash
   git commit -m "Add your awesome feature"
   ```

4. Push to the branch:
   ```bash
   git push origin feature/your-feature-name
   ```

5. Open a pull request. 🚀

## 📝 License
This project is licensed under the [MIT License](LICENSE).
