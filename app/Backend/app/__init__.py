import os
from pathlib import Path

from dotenv import load_dotenv
from flasgger import Swagger
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

# Global extensions
db = SQLAlchemy()
jwt = JWTManager()

env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)


def create_app(testing: bool = False) -> Flask:
    """Factory to create and configure the Flask app."""
    app = Flask(__name__)

    if testing:
        # Load test-specific env
        test_env = Path("Backend/tests/.env.test")
        load_dotenv(dotenv_path=test_env, override=True)
        app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("TEST_DATABASE_URL")
        app.config.update(
            TESTING=True, DEBUG=True, PROPAGATE_EXCEPTIONS=True, SQLALCHEMY_ECHO=True
        )
    else:
        db_uri = os.getenv("DATABASE_URL")
        if not db_uri:
            raise RuntimeError("DATABASE_URL not set. Check your .env file.")
        app.config["SQLALCHEMY_DATABASE_URI"] = db_uri

    # Base config
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "secret-keys")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, resources={r"/*": {"origins": "*"}})
    Swagger(app)

    # Register blueprints
    from app.routes.authentication import authentication
    from app.routes.comparison_routes import comparison
    from app.routes.group_routes import group
    from app.routes.main_routes import main
    from app.routes.personal_routes import personal

    app.register_blueprint(main, url_prefix="/api")
    app.register_blueprint(group, url_prefix="/api")
    app.register_blueprint(personal, url_prefix="/api")
    app.register_blueprint(comparison, url_prefix="/api")
    app.register_blueprint(authentication, url_prefix="/api")

    return app
