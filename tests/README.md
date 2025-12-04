# Test Suite for PCO API Wrapper

This directory contains the comprehensive test suite for the PCO API Wrapper project.

## Quick Start

```bash
# Run all unit tests
pytest tests/unit -v

# Run with coverage
pytest tests/unit -v --cov=src --cov-report=html

# Run integration tests (requires PCO credentials)
pytest tests/integration -v -m integration
```

## Directory Structure

```
tests/
├── README.md                      # This file
├── conftest.py                    # Shared pytest fixtures
├── unit/                          # Unit tests (fast, mocked)
│   ├── test_pco_helpers.py       # Tests for helper functions
│   └── test_app_endpoints.py     # Tests for Flask API endpoints
├── integration/                   # Integration tests (require API)
│   ├── test_pco_integration.py   # Real PCO API interaction tests
│   └── test_api_integration.py   # Full API workflow tests
├── fixtures/                      # Test data and mocks
│   └── mock_responses.py         # Mock PCO API responses
└── performance/                   # Performance tests
```

## Test Categories

### Unit Tests (`tests/unit/`)
- **Purpose**: Test individual functions in isolation
- **Speed**: Fast (< 30 seconds)
- **Dependencies**: None (uses mocks)
- **Coverage**: 50+ tests

**Files:**
- `test_pco_helpers.py` - Tests for all helper functions in `src/pco_helpers.py`
- `test_app_endpoints.py` - Tests for all Flask API endpoints in `src/app.py`

### Integration Tests (`tests/integration/`)
- **Purpose**: Test real API interactions and workflows
- **Speed**: Slower (1-5 minutes)
- **Dependencies**: Requires valid PCO credentials
- **Coverage**: 30+ tests

**Files:**
- `test_pco_integration.py` - Tests real PCO API operations
- `test_api_integration.py` - Tests complete API workflows

### Fixtures (`tests/fixtures/`)
- **Purpose**: Provide reusable test data and mocks
- **Contents**: Mock API responses, test data generators

## Running Tests

### Basic Commands

```bash
# All unit tests
pytest tests/unit -v

# Specific test file
pytest tests/unit/test_pco_helpers.py -v

# Specific test class
pytest tests/unit/test_pco_helpers.py::TestAddPerson -v

# Specific test
pytest tests/unit/test_pco_helpers.py::TestAddPerson::test_add_person_success -v
```

### With Coverage

```bash
# Generate coverage report
pytest tests/unit --cov=src --cov-report=html --cov-report=term-missing

# View HTML report
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
xdg-open htmlcov/index.html  # Linux
```

### Using Test Markers

```bash
# Run only unit tests
pytest -m unit -v

# Run only integration tests
pytest -m integration -v

# Skip integration tests
pytest -m "not integration" -v

# Run slow tests
pytest -m slow -v
```

## Writing New Tests

### Unit Test Template

```python
# tests/unit/test_your_module.py
import pytest
from unittest.mock import Mock, patch
from src.your_module import your_function
from tests.fixtures.mock_responses import MOCK_DATA

class TestYourFunction:
    """Tests for your_function"""
    
    def test_success_case(self, mock_pco_client):
        """Test successful execution"""
        # Arrange
        mock_pco_client.method.return_value = MOCK_DATA
        
        # Act
        result = your_function(mock_pco_client, "param")
        
        # Assert
        assert result is not None
        assert result['key'] == 'expected_value'
    
    def test_error_case(self, mock_pco_client):
        """Test error handling"""
        # Arrange
        mock_pco_client.method.side_effect = Exception("Error")
        
        # Act
        result = your_function(mock_pco_client, "param")
        
        # Assert
        assert result is None
```

### Integration Test Template

```python
# tests/integration/test_your_integration.py
import pytest
from src.pco_helpers import get_pco_client

@pytest.mark.integration
class TestYourIntegration:
    """Integration tests for your feature"""
    
    def test_real_api_call(self):
        """Test with real API"""
        pco = get_pco_client()
        
        # Your test logic
        result = your_function(pco)
        
        assert result is not None
```

## Available Fixtures

From `conftest.py`:

- `mock_pco_client` - Mocked pypco.PCO client
- `mock_person_data` - Sample person data
- `mock_email_data` - Sample email data
- `mock_campus_data` - Sample campus data
- `mock_person_list` - List of sample people
- `flask_test_client` - Flask test client for API testing
- `mock_env_vars` - Mock environment variables
- `sample_person_attributes` - Sample person attributes

## Test Coverage Goals

| Component | Target | Status |
|-----------|--------|--------|
| pco_helpers.py | 90% | ⏳ In Progress |
| app.py | 85% | ⏳ In Progress |
| Overall | 80% | ⏳ In Progress |

## Best Practices

1. **Test Independence**: Each test should be independent
2. **Clear Names**: Use descriptive test names
3. **AAA Pattern**: Arrange, Act, Assert
4. **Mock External Calls**: Don't make real API calls in unit tests
5. **Clean Up**: Use fixtures for setup and teardown
6. **Document**: Add docstrings to complex tests

## Troubleshooting

### Tests Not Found
```bash
# Make sure you're in the project root
cd /path/to/pco-api-wrapper
pytest tests/unit -v
```

### Import Errors
```bash
# Install dependencies
pip install -r requirements.txt
```

### Integration Tests Failing
```bash
# Set PCO credentials
export PCO_APP_ID=your_app_id
export PCO_SECRET=your_secret
```

## Resources

- [Full Testing Guide](../TESTING.md)
- [Pytest Documentation](https://docs.pytest.org/)
- [Project README](../README.md)

---

For detailed testing documentation, see [TESTING.md](../TESTING.md)