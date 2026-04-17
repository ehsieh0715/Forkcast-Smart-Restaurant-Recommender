# README - How to Run Backend Integration Tests

Hi, I’m Eli, the Backend Code Lead. Here’s a simple guide on how to run the backend integration tests for our project.

---

## Prerequisites

- Python 3.12 installed.
- All dependencies installed (`pip install -r requirements.txt`).
- The backend database (PostgreSQL or Supabase) is running and accessible.
- `DATABASE_URL` environment variable set correctly for your test database.
- `pytest` installed (`pip install pytest`).

---

## Running Tests

1. Activate your virtual environment if you have one:

   ```bash
   source venv/bin/activate

2.	Set environment variables needed for testing:
DATABASE_URL="postgresql://user:password@localhost:5432/test_db"
FLASK_ENV=testing

3.	Run all backend integration tests:
pytest Backend/tests/integration

4.	To run a specific integration test file, use:
pytest Backend/tests/integration/test_group_routes_integration.py

What the Tests Do
	•	Start a Flask test client.
	•	Use a real database connection (test database).
	•	Reset database state before each test.
	•	Make real HTTP requests to the backend.
	•	Check the responses and database side effects.


Troubleshooting
	•	Verify your DATABASE_URL and test database availability.
	•	Clean or reset the test database if needed.
	•	Use verbose pytest output for more info:

pytest -v Backend/tests/integration

	•	Ask me if you get stuck. Running these tests regularly helps keep our backend solid and reliable.

— Eli (Backend Code Lead)