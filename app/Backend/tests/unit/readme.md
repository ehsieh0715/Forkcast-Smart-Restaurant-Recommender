The backend test suite is written using **pytest**. Tests are modularized to align with backend architecture (routes, utils, models).

### Current Test Coverage

Test scaffolding and logic is included for the following:

| Test File                 | Description                                                                |
|---------------------------|----------------------------------------------------------------------------|
| `test_personal.py`        | Tests personalized recommendation scoring, distance filtering, predictions |
| `test_group.py`           | Tests group session creation, Fit Score logic, preference aggregation      |
| `test_comparison.py`      | Tests comparison session lifecycle: creation, add/remove/view              |
| `test_utils.py`           | Validates helper functions across personal/group/main scoring utilities    |
| `test_model.py`           | Checks database model integrity, relationships, data consistency           |
| `test_main.py`            | Tests restaurant listing, single restaurant fetch, healthcheck routes      |
| `conftest.py`             | Centralized fixtures for shared test data, client setup, and teardown      |
| `test_data.json`          | Sample data: users, restaurants, groups, predictions, fit scores           |

### Example Test Areas

- **Personal**: Relevance and ranking of restaurant recommendations  
- **Group**: Weighted Fit Score aggregation based on member preferences  
- **Comparison**: Session expiration logic and restaurant list management  
- **Models**: Column validation, foreign key relationships, JSON fields  
- **Utils**: Matching logic, scoring helpers, distance + cuisine handling  
- **Main**: Route stability, response shapes, query filtering
