import uuid  # For generating UUIDs

import pytest  # Pytest framework for fixtures and tests
from app.models import User  # User model for creating test users

from app import db  # Database instance for setup/teardown

# -------------------------------------------------------------------
# FIXTURES
# -------------------------------------------------------------------


@pytest.fixture(scope="module", autouse=True)
def setup_database(test_app):
    """
    Ensure all database tables exist before running this test module.
    This fixture runs once before any tests in this file.
    """
    with test_app.app_context():  # Push app context
        db.create_all()  # Create tables
    yield  # Run tests
    with test_app.app_context():  # After tests
        db.drop_all()  # Drop all tables


def create_test_user(session, identifier=None):
    """
    Helper to quickly create a test user in the given session.
    Optionally pass an identifier to make username/email unique.
    Returns the new user's UUID.
    """
    unique_id = identifier if identifier else uuid.uuid4().hex[:8]  # Generate unique ID
    new_user = User(
        user_id=str(uuid.uuid4()),  # Generate UUID
        name="Test User",
        username=f"testuser_{unique_id}",
        email=f"test_{unique_id}@example.com",
        password_hash="hashed-password",
        latitude=40.7128,
        longitude=-74.0060,
    )
    session.add(new_user)  # Add to session
    session.commit()  # Commit to DB
    return new_user.user_id  # Return user_id


# -------------------------------------------------------------------
# TESTS
# -------------------------------------------------------------------


def test_create_group_session_success(client, db_session):
    """Test creating a group session with valid payload."""
    created_by = create_test_user(db_session)  # Seed a user
    payload = {"group_name": "My Test Group", "created_by": str(created_by)}
    response = client.post("api/group/session/create", json=payload)  # POST request
    assert response.status_code == 201  # Should succeed
    data = response.get_json()  # Parse response
    assert data["status"] == "success"  # Status is success
    assert data["group_name"] == "My Test Group"  # Name matches
    assert str(created_by) in data["members_json"]  # Creator appears in members_json


def test_create_group_session_missing_fields(client):
    """Test missing fields for creating group session."""
    res = client.post(
        "api/group/session/create", json={"group_name": "No Creator"}
    )  # Missing created_by
    assert res.status_code == 400  # Should fail
    res = client.post(
        "api/group/session/create", json={"created_by": str(uuid.uuid4())}
    )  # Missing group_name
    assert res.status_code == 400  # Should fail


def test_submit_preferences_success(client, db_session):
    """Test submitting preferences to a group after joining."""
    created_by = create_test_user(db_session)  # Seed creator
    group_create_resp = client.post(
        "api/group/session/create",
        json={"group_name": "Pref Group", "created_by": str(created_by)},
    )
    group_id = group_create_resp.get_json()["group_id"]  # Extract group_id
    user_id = create_test_user(db_session, "pref_user")  # Seed another user
    client.post(
        f"api/group/session/{group_id}/join", json={"user_id": str(user_id)}
    )  # Join group first
    preferences = {
        "price_level": 2,
        "cuisine_preferences": ["Italian", "Mexican"],
        "distance_preference": 5,
        "busyness_preference": 3,
        "minimum_rating": 4.0,
    }
    res = client.post(
        f"api/group/session/{group_id}/submit_preferences",
        json={"user_id": str(user_id), "preferences": preferences},
    )
    assert res.status_code == 200  # Should succeed
    data = res.get_json()
    assert data["status"] == "success"
    assert data["user_id"] == str(user_id)


def test_update_preferences_success(client, db_session):
    """Test updating preferences for a user in a group."""
    created_by = create_test_user(db_session)  # Seed creator
    group_create_resp = client.post(
        "api/group/session/create",
        json={"group_name": "UpdateGroup", "created_by": str(created_by)},
    )
    group_id = group_create_resp.get_json()["group_id"]  # Get group_id
    user_id = create_test_user(db_session, "update_user")  # Seed another user
    new_preferences = {
        "price_level": 3,
        "cuisine_preferences": ["Chinese"],
        "distance_preference": 10,
        "busyness_preference": 1,
        "minimum_rating": 3.5,
    }
    res = client.put(
        f"api/group/session/{group_id}/update_preferences",
        json={"user_id": str(user_id), "preferences": new_preferences},
    )
    assert res.status_code == 200  # Should succeed
    assert res.get_json()["status"] == "success"


def test_get_group_members_success(client, db_session):
    """Test retrieving group members."""
    created_by = create_test_user(db_session)  # Seed creator
    group_create_resp = client.post(
        "api/group/session/create",
        json={"group_name": "MembersGroup", "created_by": str(created_by)},
    )
    group_id = group_create_resp.get_json()["group_id"]  # Get group_id
    res = client.get(f"api/group/session/{group_id}/members")  # GET members
    assert res.status_code == 200  # Should succeed
    data = res.get_json()
    assert data["status"] == "success"
    members_dict = data["group"]["members"]
    assert str(created_by) in members_dict  # Creator present in members


def test_delete_group_session_success(client, db_session):
    """Test deleting a group session."""
    created_by = create_test_user(db_session)  # Seed creator
    group_create_resp = client.post(
        "api/group/session/create",
        json={"group_name": "DeleteGroup", "created_by": str(created_by)},
    )
    group_id = group_create_resp.get_json()["group_id"]  # Get group_id
    delete_resp = client.delete(f"api/group/session/{group_id}")  # Delete request
    assert delete_resp.status_code == 200  # Should succeed
    assert delete_resp.get_json()["status"] == "success"


def test_clear_group_preferences_success(client, db_session):
    """Test clearing group preferences."""
    created_by = create_test_user(db_session)  # Seed creator
    group_create_resp = client.post(
        "api/group/session/create",
        json={"group_name": "ClearGroup", "created_by": str(created_by)},
    )
    group_id = group_create_resp.get_json()["group_id"]  # Get group_id
    clear_resp = client.delete(
        f"api/group/session/{group_id}/clear"
    )  # Clear preferences
    data = clear_resp.get_json()
    assert clear_resp.status_code == 200  # Should succeed
    assert data["status"] == "success"


def test_join_group_session_success(client, db_session):
    """Test joining a group session."""
    created_by = create_test_user(db_session)  # Seed creator
    group_create_resp = client.post(
        "api/group/session/create",
        json={"group_name": "JoinGroup", "created_by": str(created_by)},
    )
    group_id = group_create_resp.get_json()["group_id"]  # Get group_id
    user_id = create_test_user(db_session, "join_user")  # Seed another user
    res = client.post(
        f"api/group/session/{group_id}/join", json={"user_id": str(user_id)}
    )  # Join group
    assert res.status_code == 200  # Should succeed
    data = res.get_json()
    assert data["status"] == "success"
    members_dict = data["group"]["members"]
    assert str(user_id) in members_dict  # Joined user appears in members


def test_get_groups_by_user_success(client, db_session):
    """Test retrieving groups a user has joined."""
    creator_id = create_test_user(db_session)  # Seed creator
    user_id = create_test_user(db_session, "user_for_groups")  # Seed another user
    group_create_resp = client.post(
        "api/group/session/create",
        json={"group_name": "UserGroups", "created_by": str(creator_id)},
    )
    group_id = group_create_resp.get_json()["group_id"]  # Get group_id
    client.post(
        f"api/group/session/{group_id}/join", json={"user_id": str(user_id)}
    )  # Join group
    client.post(
        f"api/group/session/{group_id}/submit_preferences",
        json={  # Submit prefs
            "user_id": str(user_id),
            "preferences": {"price_level": 1},
        },
    )
    res = client.get(f"api/group/user/{user_id}/groups")  # Get user groups
    data = res.get_json()
    assert res.status_code == 200  # Should succeed
    assert data["status"] == "success"
    assert any(
        g["group_name"] == "UserGroups" for g in data["groups"]
    )  # Group name present


def test_group_session_results_empty(client, db_session):
    """Test group session results returns empty recommendations."""
    creator_id = create_test_user(db_session)  # Seed creator
    resp = client.post(
        "/api/group/session/create",
        json={"group_name": "ResultsGroup", "created_by": str(creator_id)},
    )
    group_id = resp.get_json()["group_id"]  # Get group_id
    res = client.get(
        f"/api/group/session/{group_id}/results?latitude=40.7&longitude=-74.0&desired_datetime=2025-07-19T12:00:00Z"
    )
    data = res.get_json()
    assert res.status_code == 200  # Should succeed
    assert data["status"] == "success"
    assert isinstance(data["recommendations"], list)  # Should return a list
