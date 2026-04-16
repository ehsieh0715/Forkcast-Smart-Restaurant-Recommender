#!/usr/bin/env python3
"""
Test script for authentication endpoints.
Run this to test the authentication system with sample data.

Make sure your Flask server is running at the specified BASE_URL before running this.
"""

import json

import pytest
import requests

from app import db


@pytest.fixture(scope="session", autouse=True)
def setup_database(test_app):
    # Create tables once before tests start
    with test_app.app_context():
        db.create_all()
    yield
    # Optionally drop tables after all tests finish
    with test_app.app_context():
        db.drop_all()


# Base URL - adjust if your server uses a different host/port
BASE_URL = "http://localhost:5000"


def test_signup():
    """Test user signup endpoint."""
    print("Testing signup...")

    signup_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
        "name": "Test User",
    }

    try:
        response = requests.post(f"{BASE_URL}/authentication/signup", json=signup_data)
        print(f"Status Code: {response.status_code}")

        try:
            response_json = response.json()
            print(f"Response JSON:\n{json.dumps(response_json, indent=2)}")
        except json.JSONDecodeError:
            print(f"Response (not JSON): {response.text}")

        print("-" * 50)
        return response
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Flask server is not running!")
        print("   Please start the server with: python run.py")
        return None


def test_login():
    """Test user login endpoint."""
    print("Testing login...")

    login_data = {"username": "testuser", "password": "password123"}

    try:
        response = requests.post(f"{BASE_URL}/authentication/login", json=login_data)
        print(f"Status Code: {response.status_code}")

        try:
            response_json = response.json()
            print(f"Response JSON:\n{json.dumps(response_json, indent=2)}")

            if response.status_code == 200:
                return response_json.get("access_token")
        except json.JSONDecodeError:
            print(f"Response (not JSON): {response.text}")

        print("-" * 50)
        return None
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Flask server is not running!")
        return None


def test_get_profile(token):
    """Test retrieving the user profile."""
    print("Testing get profile...")

    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(f"{BASE_URL}/authentication/profile", headers=headers)
        print(f"Status Code: {response.status_code}")

        try:
            response_json = response.json()
            print(f"Response JSON:\n{json.dumps(response_json, indent=2)}")
        except json.JSONDecodeError:
            print(f"Response (not JSON): {response.text}")

        print("-" * 50)
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Flask server is not running!")


def test_update_profile(token):
    """Test updating the user profile."""
    print("Testing update profile...")

    update_data = {
        "name": "Updated Test User",
        "latitude": 53.3498,
        "longitude": -6.2603,
    }

    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.put(
            f"{BASE_URL}/authentication/profile", json=update_data, headers=headers
        )
        print(f"Status Code: {response.status_code}")

        try:
            response_json = response.json()
            print(f"Response JSON:\n{json.dumps(response_json, indent=2)}")
        except json.JSONDecodeError:
            print(f"Response (not JSON): {response.text}")

        print("-" * 50)
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Flask server is not running!")


def main():
    """Run all authentication tests in order."""
    print("Authentication API Tests")
    print("=" * 50)

    signup_response = test_signup()
    if signup_response is None:
        print("❌ Cannot continue tests - server not running")
        return

    token = test_login()
    if token:
        test_get_profile(token)
        test_update_profile(token)
    else:
        print("Login failed, skipping profile tests")


if __name__ == "__main__":
    main()
