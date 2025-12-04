# Testing Guide for PCO API Wrapper

## Table of Contents
- [Overview](#overview)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Writing Tests](#writing-tests)
- [Test Coverage](#test-coverage)
- [CI/CD Integration](#cicd-integration)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Overview

This project uses **pytest** as the testing framework with comprehensive unit and integration tests. The test suite ensures code quality, reliability, and maintainability.

### Test Statistics
- **Unit Tests**: 50+ tests covering core functionality
- **Integration Tests**: 30+ tests for real API interactions
- **Target Coverage**: 80%+ code coverage
- **Test Execution Time**: ~30 seconds (unit tests)

---

## Test Structure

```
tests/
├── __init__.py
├── conftest.py                    # Shared fixtures and configuration
├── pytest.ini                     # Pytest configuration (in root)
├── unit/                          # Unit tests (fast, mocked)
│   ├── __init__.py
│   ├── test_pco_helpers.py       # Tests for pco_helpers.py
│   └── test_app_endpoints.py     # Tests for Flask endpoints
├── integration/                   # Integration tests (require API)
│   ├── __init__.py
│   ├── test_pco_integration.py   # Real PCO API tests
│   └── test_api_integration.py   # Full API workflow tests
├── fixtures/                      # Test data and mocks
│   ├── __init__.py
│   └── mock_responses.py         # Mock PCO API responses
└── performance/                   # Performance tests
    └── __init__.py
```

---

## Running Tests

### Prerequisites

```bash
# Install test dependencies
pip install -r requirements.txt
```

### Quick Start

```bash
# Run all unit tests (recommended for development)
pytest tests/unit -v

# Run with coverage
pytest tests/unit -v --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_pco_helpers.py -v

# Run specific test
pytest tests/unit/test_pco_helpers.py::TestAddPerson::test_add_person_success -v
```

### Using the Test Runner Script

```bash
# Quick test run (unit tests only, no coverage)
python run_tests.py quick

# Unit tests with coverage
python run_tests.py unit

# Integration tests (requires PCO credentials)
python run_tests.py integration

# All tests
python run_tests.py all

# Detailed coverage report
python run_tests.py coverage
```

### Test Types

#### 1. Unit Tests (Fast, No External Dependencies)
```bash
# Run only unit tests
pytest tests/unit -v

# Run with markers
pytest -m unit -v
```

**Characteristics:**
- ✅ Fast execution (< 30 seconds)
- ✅ No external API calls
- ✅ Uses mocked PCO client
- ✅ Can run offline
- ✅ Ideal for TDD and rapid development

#### 2. Integration Tests (Require PCO API Access)
```bash
# Run only integration tests
pytest tests/integration -v -m integration

# Set credentials via environment
export PCO_APP_ID=your_app_id
export PCO_SECRET=your_secret
pytest tests/integration -v -m integration
```

**Characteristics:**
- ⚠️ Slower execution (1-5 minutes)
- ⚠️ Requires valid PCO credentials
- ⚠️ Makes real API calls
- ⚠️ May create/delete test data
- ✅ Tests real-world scenarios

#### 3. Performance Tests
```bash
# Run performance tests
pytest tests/performance -v -m performance
```

---

## Writing Tests

### Unit Test Example

```python
# tests/unit/test_pco_helpers.py
import pytest
from unittest.mock import Mock
from src.pco_helpers import find_person_by_name
from tests.fixtures.mock_responses import MOCK_PERSON_RESPONSE

def test_find_person_by_name_found(mock_pco_client):
    """Test finding a person that exists"""
    # Arrange
    mock_pco_client.iterate.return_value = [MOCK_PERSON_RESPONSE]
    
    # Act
    result = find_person_by_name(mock_pco_client, "John", "Doe")
    
    # Assert
    assert result is not None
    assert result['id'] == '12345'
    assert result['attributes']['first_name'] == 'John'
```

### Integration Test Example

```python
# tests/integration/test_pco_integration.py
import pytest
from src.pco_helpers import get_pco_client, add_person, delete_person

@pytest.mark.integration
def test_create_and_delete_person():
    """Test creating and deleting a person"""
    pco = get_pco_client()
    
    # Create
    person = add_person(pco, "Test", "User", "Male")
    assert person is not None
    person_id = person['id']
    
    try:
        # Verify
        assert person['attributes']['first_name'] == "Test"
    finally:
        # Cleanup
        delete_person(pco, person_id)
```

### Using Fixtures

```python
def test_with_fixtures(mock_pco_client, mock_person_data):
    """Test using shared fixtures"""
    mock_pco_client.get.return_value = mock_person_data
    
    # Your test logic here
    result = get_person_by_id(mock_pco_client, "12345")
    assert result is not None
```

### Available Fixtures

From `tests/conftest.py`:
- `mock_pco_client` - Mocked PCO client
- `mock_person_data` - Sample person data
- `mock_email_data` - Sample email data
- `mock_campus_data` - Sample campus data
- `flask_test_client` - Flask test client
- `mock_env_vars` - Mock environment variables

---

## Test Coverage

### Viewing Coverage Reports

```bash
# Generate HTML coverage report
pytest tests/unit --cov=src --cov-report=html

# Open in browser
# Windows
start htmlcov/index.html

# macOS
open htmlcov/index.html

# Linux
xdg-open htmlcov/index.html
```

### Coverage Goals

| Component | Target | Current |
|-----------|--------|---------|
| pco_helpers.py | 90% | TBD |
| app.py | 85% | TBD |
| Overall | 80% | TBD |

### Improving Coverage

1. **Identify uncovered lines:**
   ```bash
   pytest tests/unit --cov=src --cov-report=term-missing
   ```

2. **Focus on critical paths:**
   - Error handling
   - Edge cases
   - Business logic

3. **Add tests for uncovered code:**
   ```python
   def test_error_handling():
       """Test error scenarios"""
       with pytest.raises(ValueError):
           # Test code that should raise error
           pass
   ```

---

## CI/CD Integration

### GitHub Actions

The project includes automated testing via GitHub Actions (`.github/workflows/tests.yml`):

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests
- Manual workflow dispatch

**Jobs:**
1. **Unit Tests** - Runs on Python 3.9, 3.10, 3.11, 3.12
2. **Integration Tests** - Runs on push (requires secrets)
3. **Code Quality** - Linting, formatting, type checking
4. **Security Scan** - Safety and Bandit scans

### Setting Up Secrets

For integration tests in CI/CD:

1. Go to GitHub repository → Settings → Secrets
2. Add secrets:
   - `PCO_APP_ID` - Your PCO Application ID
   - `PCO_SECRET` - Your PCO Secret

### Local CI Simulation

```bash
# Run the same checks as CI
pytest tests/unit -v --cov=src --cov-report=term-missing --cov-fail-under=80
flake8 src/
black --check src/
mypy src/ --ignore-missing-imports
```

---

## Best Practices

### 1. Test Naming Convention

```python
# Good
def test_add_person_success():
    """Test successfully adding a new person"""
    pass

def test_add_person_duplicate_check():
    """Test duplicate person detection"""
    pass

# Bad
def test1():
    pass

def test_person():
    pass
```

### 2. Arrange-Act-Assert Pattern

```python
def test_example():
    # Arrange - Set up test data and mocks
    mock_client = Mock()
    mock_client.get.return_value = {'data': {'id': '123'}}
    
    # Act - Execute the function being tested
    result = get_person_by_id(mock_client, '123')
    
    # Assert - Verify the results
    assert result is not None
    assert result['id'] == '123'
```

### 3. Test Independence

```python
# Good - Each test is independent
def test_create_person():
    person = create_person()
    assert person is not None

def test_update_person():
    person = create_person()  # Create fresh data
    update_person(person['id'])
    assert True

# Bad - Tests depend on each other
person_id = None

def test_create_person():
    global person_id
    person = create_person()
    person_id = person['id']

def test_update_person():
    update_person(person_id)  # Depends on previous test
```

### 4. Mock External Dependencies

```python
# Good - Mock external API
@patch('src.pco_helpers.pypco.PCO')
def test_with_mock(mock_pco):
    mock_pco.return_value.get.return_value = {'data': {}}
    # Test logic

# Bad - Make real API calls in unit tests
def test_without_mock():
    pco = pypco.PCO(app_id, secret)  # Real API call
    result = pco.get('/people/v2/people/123')
```

### 5. Test Error Cases

```python
def test_error_handling():
    """Test that errors are handled gracefully"""
    mock_client = Mock()
    mock_client.get.side_effect = Exception("API Error")
    
    result = get_person_by_id(mock_client, '123')
    assert result is None  # Should handle error gracefully
```

### 6. Use Descriptive Assertions

```python
# Good
assert person['first_name'] == 'John', "First name should be John"
assert len(emails) > 0, "Person should have at least one email"

# Bad
assert person
assert emails
```

---

## Troubleshooting

### Common Issues

#### 1. Import Errors

**Problem:**
```
ModuleNotFoundError: No module named 'pytest'
```

**Solution:**
```bash
pip install -r requirements.txt
```

#### 2. Coverage Not Working

**Problem:**
```
Coverage.py warning: No data was collected
```

**Solution:**
```bash
# Ensure you're running from project root
cd /path/to/pco-api-wrapper
pytest tests/unit --cov=src
```

#### 3. Integration Tests Failing

**Problem:**
```
ValueError: PCO_APP_ID and PCO_SECRET must be set
```

**Solution:**
```bash
# Set environment variables
export PCO_APP_ID=your_app_id
export PCO_SECRET=your_secret

# Or use .env file
cp .env.example .env
# Edit .env with your credentials
```

#### 4. Tests Running Slowly

**Problem:** Tests take too long to run

**Solution:**
```bash
# Run only unit tests (fast)
pytest tests/unit -v

# Skip integration tests
pytest tests/ -v -m "not integration"

# Run in parallel (requires pytest-xdist)
pip install pytest-xdist
pytest tests/unit -v -n auto
```

#### 5. Flaky Tests

**Problem:** Tests pass sometimes, fail other times

**Solution:**
- Check for test dependencies
- Ensure proper cleanup in fixtures
- Use `pytest-rerunfailures` for retry logic:
  ```bash
  pip install pytest-rerunfailures
  pytest tests/ --reruns 3
  ```

---

## Test Markers

Use markers to categorize and run specific test types:

```python
# Mark as unit test
@pytest.mark.unit
def test_something():
    pass

# Mark as integration test
@pytest.mark.integration
def test_api_call():
    pass

# Mark as slow test
@pytest.mark.slow
def test_long_running():
    pass
```

Run specific markers:
```bash
# Run only unit tests
pytest -m unit

# Run everything except integration
pytest -m "not integration"

# Run slow tests
pytest -m slow
```

---

## Continuous Improvement

### Adding New Tests

1. **Identify untested code:**
   ```bash
   pytest --cov=src --cov-report=term-missing
   ```

2. **Write test for new feature:**
   ```python
   def test_new_feature():
       """Test description"""
       # Test implementation
       pass
   ```

3. **Run tests:**
   ```bash
   pytest tests/unit/test_new_feature.py -v
   ```

4. **Verify coverage:**
   ```bash
   pytest --cov=src --cov-report=html
   ```

### Test Maintenance

- **Review tests regularly** - Remove obsolete tests
- **Update mocks** - Keep mock data current with API changes
- **Refactor duplicates** - Extract common test logic to fixtures
- **Document complex tests** - Add clear docstrings

---

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Python Testing Best Practices](https://docs.python-guide.org/writing/tests/)
- [PCO API Documentation](https://developer.planning.center/docs/)

---

## Getting Help

If you encounter issues:

1. Check this documentation
2. Review test examples in `tests/` directory
3. Check GitHub Actions logs for CI failures
4. Create an issue in the repository

---

**Last Updated:** 2025-11-22  
**Version:** 1.0.0