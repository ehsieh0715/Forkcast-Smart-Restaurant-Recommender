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
  Smart Restaurant Recommender (dev branch)
  ├── app/
  │   ├── Frontend/        # See Frontend README for details
  │   ├── Backend/
  │   │   ├── app/
  │   │   │   ├── __init__.py               # Flask app initialization and Blueprints
  │   │   │   ├── models.py                 # SQLAlchemy models
  │   │   │   ├── routes/
  │   │   │   │   ├── main_routes.py
  │   │   │   │   ├── personal_routes.py
  │   │   │   │   ├── group_routes.py
  │   │   │   │   ├── authentication.py
  │   │   │   │   └── comparison_routes.py
  │   │   │   ├── utils/
  │   │   │   │   ├── main_utils.py
  │   │   │   │   ├── personal_utils.py
  │   │   │   │   ├── group_utils.py
  │   │   │   │   ├── comparison_utils.py
  │   │   │   │   └── authentication_utils.py
  │   │   │   └── tests/
  │   │   │       ├── conftest.py
  │   │   │       ├── integration/
  │   │   │       └── unit/
  │   │   ├── Dockerfile
  │   │   ├── requirements.txt
  │   │   ├── run.py
  │   │   └── README.md
  │   │
  │   ├── data/
  │   │   ├── data_preparation/
  │   │   │   ├── yellow_taxi/
  │   │   │   ├── citi_bike/
  │   │   │   ├── mta_subway/
  │   │   │   ├── manhattan_grid/
  │   │   │   ├── bike_subway_grid_overlap/
  │   │   │   ├── inspection/
  │   │   │   ├── restaurant_data_fetching/
  │   │   │   ├── wheelchair_accessibility/
  │   │   │   ├── event_data/
  │   │   │   ├── holiday_module/
  │   │   │   ├── hourly_weather/
  │   │   │   ├── population/
  │   │   │   └── prepared_outputs/
  │   │   │
  │   │   ├── model_development/
  │   │   │   ├── notebooks/
  │   │   │   ├── models/
  │   │   │   └── datasets/
  │   │   │
  │   │   ├── script/
  │   │   │   ├── db/
  │   │   │   ├── fetchers/
  │   │   │   └── model/
  │   │   │
  │   │   ├── environment.yml
  │   │   ├── example.env
  │   │   └── README.md
  │   │
  │   └── nginx/
  │       ├── default.conf
  │       └── Dockerfile
  │
  ├── documents/
  │   ├── tests/
  │   ├── Github_Workflow.md
  │   └── System Structure.png
  │
  ├── .github/workflows/
  ├── .gitignore
  ├── .dockerignore
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
