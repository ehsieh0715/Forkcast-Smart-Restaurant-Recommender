import os
import sys
import uuid

import pytest
from dotenv import load_dotenv
from flask_jwt_extended import create_access_token
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

# Load environment variables from `.env.test`
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env.test"))

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from app.models import User

from app import create_app, db


@pytest.fixture(scope="session")
def test_app():
    """
    Initializes the Flask app once per test session,
    points to TEST_DATABASE_URL, and ensures all tables exist.
    """
    app = create_app(testing=True)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("TEST_DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["TESTING"] = True

    with app.app_context():
        should_reset = os.getenv("RESET_DB", "false").lower() == "true"

        if should_reset:
            print("🧪 RESET_DB=true → dropping and recreating all tables")
            tables_to_drop = [
                "personal_fit_scores",
                "group_fit_scores",
                "busyness_predictions",
                "comparison_sessions",
                "groups",
                "restaurants",
                "users",
                "holiday",
                "restaurant_popular_hour",
                "restaurant_opening_hour",
                "grid_info",
                "location_mapping",
            ]
            for t in tables_to_drop:
                db.session.execute(text(f"DROP TABLE IF EXISTS {t} CASCADE"))
            db.session.commit()
            db.create_all()
        else:
            print("⚠️ RESET_DB not enabled → ensuring tables exist")
            db.create_all()

    return app


@pytest.fixture()
def client(test_app):
    """
    Provides a Flask test client to send requests.
    """
    return test_app.test_client()


@pytest.fixture()
def db_session(test_app):
    """
    Creates a new SQLAlchemy session bound to a SAVEPOINT for each test.
    Rolls back after test finishes so no data leaks between tests.
    """
    with test_app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()

        # Use SQLAlchemy sessionmaker for compatibility
        Session = sessionmaker(bind=connection)
        session = Session()

        # Swap out the db.session for this test
        old_session = db.session
        db.session = session

        try:
            yield session
        finally:
            # Roll back everything done in the test
            session.close()
            transaction.rollback()
            connection.close()
            # Restore the original session
            db.session = old_session


@pytest.fixture()
def token(test_app):
    """
    Creates a temporary user and returns a valid JWT for testing.
    """
    with test_app.app_context():
        unique_id = uuid.uuid4().hex[:8]
        user = User(
            user_id=uuid.uuid4(),
            name="Test User",
            username=f"testuser_{unique_id}",
            email=f"test_{unique_id}@example.com",
            password_hash="hashed-password",
            latitude=40.7128,
            longitude=-74.0060,
        )
        db.session.add(user)
        db.session.commit()
        return create_access_token(identity=user.user_id)
