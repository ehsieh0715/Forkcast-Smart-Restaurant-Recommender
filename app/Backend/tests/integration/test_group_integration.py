import uuid  # Used to generate unique identifiers
from datetime import datetime, timezone  # Used for timestamps in UTC

import pytest  # Pytest framework for writing and running tests
from app.models import (  # Import database models used in tests
    BusynessPrediction, Group, Restaurant, User)

# ----------------------------------------------
# Helper Functions
# ----------------------------------------------


def create_test_user(db_session, user_id=None):
    """Create and commit a test user into the provided database session."""  # Docstring explaining function
    user = User(  # Create a new User instance with test data
        user_id=user_id or uuid.uuid4(),  # Use provided UUID or generate a new one
        name="Test User",  # Set name field
        username=f"testuser_{uuid.uuid4().hex[:8]}",  # Generate unique username
        email=f"test_{uuid.uuid4().hex[:8]}@example.com",  # Generate unique email
        password_hash="hashed-password",  # Set dummy password
        latitude=40.7128,  # Set latitude
        longitude=-74.006,  # Set longitude
    )
    db_session.add(user)  # Add user to database session
    db_session.commit()  # Commit session to persist user
    return user.user_id  # Return user_id to caller


def iso_now():
    """Return the current UTC time as an ISO 8601 formatted string."""  # Docstring
    return datetime.now(
        timezone.utc
    ).isoformat()  # Return current UTC time as ISO string


# ----------------------------------------------
# Integration Tests for Group Routes
# ----------------------------------------------
@pytest.mark.usefixtures("db_session")  # Use the db_session fixture for setup/teardown
class TestGroupRoutesIntegration:  # Define test class for Group routes
    """Integration tests for all Group route endpoints."""  # Docstring for the test class

    def test_create_group_session_success(self, client, db_session):  # Test method
        """Test creating a group session with valid data."""  # Docstring
        created_by_uuid = uuid.uuid4()  # Generate a UUID for creator
        create_test_user(db_session, user_id=created_by_uuid)  # Seed test user in DB
        payload = {  # Prepare payload for group creation
            "group_name": "Test Group",  # Name of the group
            "created_by": str(created_by_uuid),  # ID of the creator
        }
        res = client.post(
            "api/group/session/create", json=payload
        )  # POST request to create group
        assert (
            res.status_code == 201
        ), f"Failed to create group: {res.get_data(as_text=True)}"  # Assert HTTP status
        data = res.get_json()  # Parse JSON response
        assert "group_id" in data  # Ensure group_id is present
        assert data["group_name"] == "Test Group"  # Ensure group_name matches
        assert (
            str(created_by_uuid) in data["members_json"]
        )  # Ensure creator is in members_json
        assert (
            "user_name" in data["members_json"][str(created_by_uuid)]
        )  # Ensure user_name key exists
        assert (
            data["members_json"][str(created_by_uuid)]["user_name"] == "Test User"
        )  # Ensure name matches

    def test_create_group_session_missing_fields(self, client):  # Test method
        """Test creating a group session with missing fields."""  # Docstring
        res = client.post(
            "api/group/session/create", json={"group_name": "No Creator"}
        )  # Missing created_by
        assert res.status_code == 400  # Should return bad request
        data = res.get_json()  # Parse response
        assert data["status"] == "error"  # Should return error status
        res = client.post(
            "api/group/session/create", json={"created_by": str(uuid.uuid4())}
        )  # Missing group_name
        assert res.status_code == 400  # Should return bad request
        data = res.get_json()  # Parse response
        assert data["status"] == "error"  # Should return error status

    def test_submit_preferences_success(self, client, db_session):  # Test method
        """Test submitting preferences successfully."""  # Docstring
        created_by = uuid.uuid4()  # Generate creator ID
        create_test_user(db_session, user_id=created_by)  # Seed user
        group = {  # Prepare group payload
            "group_name": "Pref Group",  # Group name
            "created_by": str(created_by),  # Creator ID
        }
        res = client.post("api/group/session/create", json=group)  # Create group
        assert res.status_code == 201  # Should succeed
        group_id = res.get_json()["group_id"]  # Extract group_id
        user_id = create_test_user(db_session)  # Create another user
        join_res = client.post(
            f"api/group/session/{group_id}/join", json={"user_id": str(user_id)}
        )  # Join group
        assert join_res.status_code == 200  # Should succeed
        prefs = {  # Prepare preferences payload
            "cuisine_preferences": ["Italian", "Mexican"],  # Preferred cuisines
            "distance_preference": 500,  # Preferred distance
            "busyness_preference": 3,  # Preferred busyness
            "minimum_rating": 4.0,  # Minimum rating
            "price_level": 2,  # Price level
        }
        response = client.post(
            f"api/group/session/{group_id}/submit_preferences",
            json={"user_id": str(user_id), "preferences": prefs},
        )  # Submit preferences
        assert response.status_code == 200  # Should succeed
        data = response.get_json()  # Parse response
        assert data["status"] == "success"  # Status should be success
        assert data["user_id"] == str(user_id)  # User ID should match

    def test_submit_preferences_invalid_price_level(
        self, client, db_session
    ):  # Test method
        """Test submitting preferences with invalid price_level."""  # Docstring
        created_by = uuid.uuid4()  # Generate creator ID
        create_test_user(db_session, user_id=created_by)  # Seed user
        res = client.post(
            "api/group/session/create",
            json={"group_name": "Test", "created_by": str(created_by)},
        )  # Create group
        assert res.status_code == 201  # Should succeed
        group_id = res.get_json()["group_id"]  # Get group_id
        prefs = {"price_level": 5}  # Invalid price level
        response = client.post(
            f"api/group/session/{group_id}/submit_preferences",
            json={"preferences": prefs},
        )  # Submit
        assert response.status_code == 400  # Should fail
        data = response.get_json()  # Parse response
        assert (
            "price_level" in data["message"]
        )  # Error message should mention price_level

    def test_update_preferences_success(self, client, db_session):  # Test method
        """Test updating preferences successfully."""  # Docstring
        created_by = uuid.uuid4()  # Generate creator
        create_test_user(db_session, user_id=created_by)  # Seed user
        res = client.post(
            "api/group/session/create",
            json={"group_name": "UpdateGroup", "created_by": str(created_by)},
        )  # Create group
        assert res.status_code == 201  # Should succeed
        group_id = res.get_json()["group_id"]  # Get group_id
        user_id = create_test_user(db_session)  # Seed new user
        join_res = client.post(
            f"api/group/session/{group_id}/join", json={"user_id": str(user_id)}
        )  # Join group
        assert join_res.status_code == 200  # Should succeed
        prefs = {  # Initial preferences
            "cuisine_preferences": ["Chinese"],
            "distance_preference": 300,
            "busyness_preference": 2,
            "minimum_rating": 3.5,
            "price_level": 1,
        }
        sub_res = client.post(
            f"api/group/session/{group_id}/submit_preferences",
            json={"user_id": str(user_id), "preferences": prefs},
        )  # Submit preferences
        assert sub_res.status_code == 200  # Should succeed
        new_prefs = {  # Updated preferences
            "cuisine_preferences": ["Japanese"],
            "distance_preference": 1000,
            "busyness_preference": 4,
            "minimum_rating": 4.5,
            "price_level": 3,
        }
        response = client.put(
            f"api/group/session/{group_id}/update_preferences",
            json={"user_id": str(user_id), "preferences": new_prefs},
        )  # Update preferences
        assert response.status_code == 200  # Should succeed
        data = response.get_json()  # Parse response
        assert data["status"] == "success"  # Status should be success

    def test_update_preferences_invalid_payload(self, client):  # Test method
        """Test updating preferences with invalid payload."""  # Docstring
        response = client.put(
            "api/group/session/00000000-0000-0000-0000-000000000000/update_preferences",
            json={"preferences": {"price_level": 1}},
        )  # Missing user_id
        assert response.status_code == 400  # Should fail
        response = client.put(
            "api/group/session/00000000-0000-0000-0000-000000000000/update_preferences",
            json={"user_id": "user", "preferences": "not-a-dict"},
        )  # Invalid preferences
        assert response.status_code == 400  # Should fail

    def test_get_group_members_success(self, client, db_session):  # Test method
        """Test retrieving members of a group."""  # Docstring
        created_by = uuid.uuid4()  # Generate creator
        create_test_user(db_session, user_id=created_by)  # Seed user
        res = client.post(
            "api/group/session/create",
            json={"group_name": "MembersGroup", "created_by": str(created_by)},
        )  # Create group
        assert res.status_code == 201  # Should succeed
        group_id = res.get_json()["group_id"]  # Get group_id
        user1 = create_test_user(db_session)  # Create first user
        client.post(
            f"api/group/session/{group_id}/join", json={"user_id": str(user1)}
        )  # User1 joins
        client.post(
            f"api/group/session/{group_id}/submit_preferences",
            json={"user_id": str(user1), "preferences": {"price_level": 1}},
        )  # User1 submits prefs
        user2 = create_test_user(db_session)  # Create second user
        client.post(
            f"api/group/session/{group_id}/join", json={"user_id": str(user2)}
        )  # User2 joins
        client.post(
            f"api/group/session/{group_id}/submit_preferences",
            json={"user_id": str(user2), "preferences": {"price_level": 2}},
        )  # User2 submits prefs
        response = client.get(f"api/group/session/{group_id}/members")  # Get members
        assert response.status_code == 200  # Should succeed
        data = response.get_json()  # Parse response
        members_dict = data["group"]["members"]  # Extract members dict
        assert str(user1) in members_dict  # Ensure user1 present
        assert str(user2) in members_dict  # Ensure user2 present

    def test_clear_group_preferences_success(self, client, db_session):  # Test method
        """Test clearing preferences in a group."""  # Docstring
        created_by = uuid.uuid4()  # Generate creator
        create_test_user(db_session, user_id=created_by)  # Seed user
        res = client.post(
            "api/group/session/create",
            json={"group_name": "ClearGroup", "created_by": str(created_by)},
        )  # Create group
        assert res.status_code == 201  # Should succeed
        group_id = res.get_json()["group_id"]  # Get group_id
        user_id = create_test_user(db_session)  # Create new user
        client.post(
            f"api/group/session/{group_id}/join", json={"user_id": str(user_id)}
        )  # User joins
        client.post(
            f"api/group/session/{group_id}/submit_preferences",
            json={"user_id": str(user_id), "preferences": {"price_level": 2}},
        )  # User submits prefs
        response = client.delete(
            f"api/group/session/{group_id}/clear"
        )  # Clear preferences
        assert response.status_code == 200  # Should succeed
        data = response.get_json()  # Parse response
        assert data["status"] == "success"  # Should be success

    def test_delete_group_session_success(self, client, db_session):  # Test method
        """Test deleting a group session."""  # Docstring
        created_by = uuid.uuid4()  # Generate creator
        create_test_user(db_session, user_id=created_by)  # Seed user
        res = client.post(
            "api/group/session/create",
            json={"group_name": "DeleteGroup", "created_by": str(created_by)},
        )  # Create group
        assert res.status_code == 201  # Should succeed
        group_id = res.get_json()["group_id"]  # Get group_id
        response = client.delete(f"api/group/session/{group_id}")  # Delete group
        assert response.status_code == 200  # Should succeed
        data = response.get_json()  # Parse response
        assert data["status"] == "success"  # Should be success
        grp = (
            db_session.query(Group).filter_by(group_id=uuid.UUID(group_id)).first()
        )  # Query DB
        assert grp is None  # Ensure group deleted

    def test_group_session_results(self, client, db_session):  # Test method
        """Test retrieving recommendations for a group session."""  # Docstring
        created_by = uuid.uuid4()  # Generate creator
        create_test_user(db_session, user_id=created_by)  # Seed user
        group = Group(
            group_name="ResultsGroup",
            created_by=created_by,
            members_json={str(created_by): {}},
        )  # Create group object
        db_session.add(group)  # Add to session
        rest_grid_id = "grid_123"  # Set grid ID
        restaurant = Restaurant(
            restaurant_id=uuid.uuid4(),
            place_id="place_abc",
            full_name="Test Restaurant",
            lat=40.7128,
            lon=-74.0060,
            grid_id=rest_grid_id,
        )  # Create restaurant
        db_session.add(restaurant)  # Add restaurant
        pred = BusynessPrediction(
            grid_id=rest_grid_id,
            timestamp=datetime.now(timezone.utc),
            predicted_level=3,
        )  # Create prediction
        db_session.add(pred)  # Add prediction
        db_session.commit()  # Commit all to DB
        group_id = str(group.group_id)  # Get group_id
        params = {
            "latitude": "40.7128",
            "longitude": "-74.0060",
            "desired_datetime": iso_now(),
        }  # Build query params
        response = client.get(
            f"api/group/session/{group_id}/results", query_string=params
        )  # GET results
        assert response.status_code == 200  # Should succeed
        data = response.get_json()  # Parse response
        assert data["status"] == "success"  # Should be success
        assert isinstance(data["recommendations"], list)  # Should be a list
        assert any(
            r["full_name"] == "Test Restaurant" for r in data["recommendations"]
        )  # Ensure restaurant appears

    def test_group_session_results_missing_params(self, client):  # Test method
        """Test missing params when retrieving group session results."""  # Docstring
        response = client.get(
            "api/group/session/00000000-0000-0000-0000-000000000000/results"
        )  # GET without params
        assert response.status_code == 400  # Should fail
        data = response.get_json()  # Parse response
        assert data["status"] == "error"  # Should be error

    def test_join_group_session_success(self, client, db_session):  # Test method
        """Test joining a group session successfully."""  # Docstring
        created_by = uuid.uuid4()  # Generate creator
        create_test_user(db_session, user_id=created_by)  # Seed user
        res = client.post(
            "api/group/session/create",
            json={"group_name": "JoinGroup", "created_by": str(created_by)},
        )  # Create group
        assert res.status_code == 201  # Should succeed
        group_id = res.get_json()["group_id"]  # Get group_id
        user_id = create_test_user(db_session)  # Create user
        response = client.post(
            f"api/group/session/{group_id}/join", json={"user_id": str(user_id)}
        )  # Join group
        assert response.status_code == 200  # Should succeed
        data = response.get_json()  # Parse response
        assert data["status"] == "success"  # Should be success
        assert (
            str(user_id) in data["group"]["members"]
        )  # Ensure user present in members

    def test_join_group_session_missing_user_id(self, client):  # Test method
        """Test joining a group session with missing user_id."""  # Docstring
        response = client.post(
            "api/group/session/00000000-0000-0000-0000-000000000000/join", json={}
        )  # POST without user_id
        assert response.status_code == 400  # Should fail
        data = response.get_json()  # Parse response
        assert data["status"] == "error"  # Should be error
