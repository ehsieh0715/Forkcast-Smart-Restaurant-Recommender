# Restaurant Busyness Predictor — Frontend API Documentation

This document describes all backend API endpoints available for use by the frontend. All endpoints respond with JSON. Error responses also follow a standard JSON format.

---

## ROUTE OVERVIEW

| Category       | Endpoint                                             | Method | Description                                       |
|----------------|------------------------------------------------------|--------|---------------------------------------------------|
| Main           | /healthcheck                                         | GET    | Basic health ping                                 |
|                | /                                                    | GET    | Root greeting                                     |
|                | /restaurants                                         | GET    | All restaurants with metadata and predictions     |
|                | /restaurants/<restaurant_id>                         | GET    | Full metadata for a specific restaurant           |
|                | /restaurants/<restaurant_id>/busyness                | GET    | Busyness level for a specific restaurant          |
|                | /restaurants/predictions                             | GET    | Predictions for all restaurants                   |
|                | /restaurants/top-rated                               | GET    | Top 25 rated restaurants with predictions         |
|                | /heatmap                                             | GET    | GeoJSON heatmap of city busyness                  |
|                | /filters/options                                     | GET    | Get all filter values                             |
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
| authentication | /authentication/signup                               | POST   | Create a new user account.                        |
|                | /authentication/login                                | POST   | Authenticates user and returns JWT token.         |
|                | /authentication/profile                              | GET    | Retrieves the current user's profile information. |
|                | /authentication/profile                              | PUT    | Updates the current user's profile information    |

---

## **Main Routes**

### GET /

```json
{
  "message": "Restaurant Busyness Predictor backend is running."
}
```

### GET /restaurants

```json
{
  "status": "success",
  "restaurants": [
    {
      "restaurant_id": "uuid-string",
      "place_id": "place123",
      "full_name": "Restaurant Name",
      "inspection_id": "XYZ789",
      "image_url": "...",
      "lat": 52.123,
      "lon": -6.543,
      "phone": "...",
      "rating": 4.5,
      "review_count": 125,
      "address": "...",
      "inspection_date": "2024-08-12T00:00:00",
      "cuisine_type": "Italian",
      "cuisine_keyword": "pasta",
      "inspection_grade": "A",
      "predicted_level": 2.45
    }
  ]
}
```

### GET /restaurants/<restaurant_id>

```json
{
  "restaurant_id": "uuid-string",
  "place_id": "place123",
  "full_name": "Restaurant Name",
  "inspection_id": "XYZ789",
  "image_url": "...",
  "lat": 52.123,
  "lon": -6.543,
  "phone": "...",
  "rating": 4.5,
  "review_count": 125,
  "address": "...",
  "inspection_date": "2024-08-12T00:00:00",
  "cuisine_type": "Italian",
  "cuisine_keyword": "pasta",
  "inspection_grade": "A",
  "predicted_level": 2.45
}
```

### GET /restaurants/<restaurant_id>/busyness

```json
{
  "restaurant_id": "uuid-string",
  "full_name": "Restaurant Name",
  "grid_id": "grid-abc",
  "address": "123 Example Ave, NY",
  "predicted_level": 2.45
}
```

### GET /restaurants/predictions

```json
{
  "status": "success",
  "predictions": [
    {
      "restaurant_id": "uuid-string",
      "restaurant_full_name": "Restaurant Name",
      "predicted_busyness": 2.45,
      "timestamp": "2024-08-12T14:30:00"
    }
  ]
}
```

### GET /restaurants/top-rated

```json
{
  "status": "success",
  "count": 25,
  "restaurants": [
    {
      "restaurant_id": "uuid-string",
      "place_id": "place123",
      "full_name": "Restaurant Name",
      "rating": 4.8,
      "review_count": 320,
      "predicted_level": 2.1,
      "predicted_time": "2024-08-12T15:00:00"
    }
  ]
}
```

### GET /heatmap

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "grid_id": "grid123",
        "predicted_level": 3,
        "timestamp": "2024-08-12T12:00:00"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[...]]]
      }
    }
  ]
}
```

### GET /filters/options

```json
{
  "status": "success",
  "filters": {
    "ratings": [1, 2, 3, 4, 5],
    "review_counts": ["0+", "10", "25+", "50+", "75+", "100+"],
    "cuisine_types": ["Italian", "Chinese", "American"],
    "price_levels": ["Cheap", "Medium", "Expensive"],
    "busyness_levels": ["Low", "Medium", "High"],
    "distance_options": ["Within 500m", "Within 1km", "Within 5km", "Within 10km"]
  }
}
```

### GET /healthcheck

```json
{
  "status": "ok"
}
```

## **Personal Routes**

### GET /personal/restaurant/<restaurant_id>/prediction

```json
{
  "restaurant_id": "uuid-string",
  "grid_id": "grid123",
  "datetime": "2024-08-12T18:00:00",
  "predicted_level": 2.45
}
```

### POST /personal/recommendation

```json
{
  "location": {
    "latitude": 40.7128,
    "longitude": -74.0060
  },
  "cuisine_preferences": ["Italian", "Mexican"],
  "price_level": "Medium",
  "rating": 4.0,
  "review_count": 50,
  "desired_datetime": "2024-08-12T18:00:00",
  "busyness_level_max": 3,
  "busyness_preference": 2
}
```

Response:

```json
{
  "recommendations": [
    {
      "restaurant_id": "uuid-string",
      "name": "La Trattoria",
      "cuisine": "Italian",
      "predicted_busyness": 2.1,
      "price_level": "Medium",
      "rating": 4.3,
      "review_count": 89,
      "distance_meters": 512,
      "fit_score": 0.912
    },
    {
      "restaurant_id": "uuid-string",
      "name": "Taco Fiesta",
      "cuisine": "Mexican",
      "predicted_busyness": 1.7,
      "price_level": "Medium",
      "rating": 4.1,
      "review_count": 110,
      "distance_meters": 780,
      "fit_score": 0.873
    }
  ]
}
```

## **Group Routes**

### GET /group/session/<group_id>/results

```json
{
  "recommendations": [
    {
      "restaurant_id": "uuid-string",
      "place_id": "abc123",
      "full_name": "Joe’s Diner",
      "address": "123 Main St",
      "rating": 4.5,
      "review_count": 89,
      "cuisine_type": "Italian",
      "cuisine_keyword": "pasta",
      "inspection_grade": "A",
      "lat": 40.7128,
      "lon": -74.0060,
      "phone": "...",
      "image_url": "...",
      "fit_score": 0.921,
      "distance_meters": 524,
      "predicted_level": 2.3
    }
  ]
}
```

### POST /group/session/create

```json
{
  "group_name": "Dinner Plans",
  "created_by": "user-uuid"
}
```

Response:

```json
{
  "status": "success",
  "group_id": "uuid-string"
}
```

### DELETE /group/session/<group_id>

```json
{
  "status": "success",
  "message": "Group <group_id> deleted."
}
```

### POST /group/session/<group_id>/submit_preferences

```json
{
  "user_id": "eli123",
  "preferences": {
    "cuisine": ["Thai", "Mexican"],
    "price_level": "Cheap"
  }
}
```

Response:

```json
{
  "status": "success",
  "message": "Preferences submitted for eli123.",
  "user_id": "eli123"
}
```

### PUT /group/session/<group_id>/update_preferences

```json
{
  "user_id": "eli123",
  "preferences": {
    "cuisine": ["Korean"],
    "price_level": "Medium"
  }
}
```

Response:

```json
{
  "status": "success",
  "message": "Preferences updated for eli123."
}
```

### GET /group/session/<group_id>/members

```json
{
  "status": "success",
  "group_id": "uuid-string",
  "members": {
    "eli123": {
      "cuisine": ["Italian"],
      "price_level": "Medium"
    },
    "guest-uuid": {
      "cuisine": ["Chinese"],
      "price_level": "Cheap"
    }
  }
}
```

### DELETE /group/session/<group_id>/clear

```json
{
  "status": "success",
  "message": "All preferences cleared for group uuid-string."
}
```

### POST /group/session/<group_id>/join

```json
{
  "user_id": "guest-789",
  "preferences": {
    "cuisine": ["Mexican"],
    "price_level": "Cheap"
  }
}
```

Response:

```json
{
  "status": "success",
  "message": "User guest-789 joined group uuid-string.",
  "group_id": "uuid-string",
  "user_id": "guest-789",
  "members": {
    "guest-789": {
      "cuisine": ["Mexican"],
      "price_level": "Cheap"
    }
  }
}
```

### GET /group/user/<user_id>/groups

```json
{
  "status": "success",
  "user_id": "eli123",
  "groups": [
    {
      "group_id": "uuid-1",
      "group_name": "Team Lunch"
    },
    {
      "group_id": "uuid-2",
      "group_name": "Birthday Dinner"
    }
  ]
}
```

## **Comparison Routes**

### POST /comparison/session/create

```json
{
  "status": "success",
  "session_id": "uuid-string",
  "expires_at": "2024-08-12T14:30:00+00:00"
}
```

### POST /comparison/session/<session_id>/add_restaurant

```json
{
  "restaurant_id": "uuid-string"
}
```

Response:

```json
{
  "status": "success",
  "message": "Restaurant added to session."
}
```

### POST /comparison/session/<session_id>/remove_restaurant

```json
{
  "restaurant_id": "uuid-string"
}
```

Response:

```json
{
  "status": "success",
  "message": "Restaurant removed from session."
}
```

### POST /comparison/session/<session_id>/view

```json
{
  "status": "success",
  "session_id": "uuid-string",
  "restaurants": [
    {
      "restaurant_id": "uuid-string",
      "place_id": "abc123",
      "full_name": "Joe’s Diner",
      "address": "123 Main St",
      "rating": 4.5,
      "review_count": 89,
      "cuisine_type": "Italian",
      "cuisine_keyword": "pasta",
      "inspection_grade": "A",
      "lat": 40.7128,
      "lon": -74.0060,
      "phone": "123-456-7890",
      "image_url": "https://...",
      "google_name": "Joe’s Diner NYC",
      "predicted_level": 2.3
    }
  ]
}
```

Error:

```json
{
  "status": "error",
  "message": "Session has expired."
}
```

## **Authentication Routes**

### POST /authentication/signup

```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepassword123",
  "name": "John Doe"
}
```

Response:

```json
{
  "message": "User created successfully",
  "user_id": "uuid-string",
  "username": "john_doe",
  "email": "john@example.com",
  "name": "John Doe"
}
```

### POST /authentication/login

```json
{
  "username": "john_doe",
  "password": "securepassword123"
}
```

Response:

```json
{
  "message": "Login successful",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "user_id": "uuid-string",
    "username": "john_doe",
    "email": "john@example.com",
    "name": "John Doe"
  }
}
```

### GET /authentication/profile

Headers:
Authorization: Bearer <jwt_token>

Response:

```json
{
  "user_id": "uuid-string",
  "username": "john_doe",
  "email": "john@example.com",
  "name": "John Doe",
  "latitude": 53.3498,
  "longitude": -6.2603
}
```

### PUT /authentication/profile

Headers:
Authorization: Bearer <jwt_token>

```json
{
  "name": "John Smith",
  "latitude": 53.3498,
  "longitude": -6.2603
}
```

Response:

```json
{
  "message": "Profile updated successfully",
  "user_id": "uuid-string",
  "username": "john_doe",
  "email": "john@example.com",
  "name": "John Smith",
  "latitude": 53.3498,
  "longitude": -6.2603
}
```