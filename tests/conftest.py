"""
Pytest configuration and shared fixtures for PCO API Wrapper tests
"""

import pytest
import os
from unittest.mock import Mock, MagicMock
from dotenv import load_dotenv

# Load environment variables for tests
load_dotenv()


@pytest.fixture
def mock_pco_client():
    """
    Create a mock PCO client for unit tests.
    
    Returns:
        Mock: A mocked pypco.PCO client
    """
    mock_client = Mock()
    mock_client.get = Mock()
    mock_client.post = Mock()
    mock_client.patch = Mock()
    mock_client.delete = Mock()
    mock_client.iterate = Mock()
    mock_client.template = Mock()
    return mock_client


@pytest.fixture
def mock_person_data():
    """
    Sample person data for testing.
    
    Returns:
        dict: Mock person data structure
    """
    return {
        'data': {
            'id': '12345',
            'type': 'Person',
            'attributes': {
                'first_name': 'John',
                'last_name': 'Doe',
                'gender': 'Male',
                'birthdate': '1990-01-01',
                'status': 'active',
                'membership': 'Member',
                'created_at': '2023-01-01T00:00:00Z',
                'updated_at': '2023-06-01T00:00:00Z'
            },
            'relationships': {
                'primary_campus': {
                    'data': {
                        'id': '1',
                        'type': 'Campus'
                    }
                }
            }
        }
    }


@pytest.fixture
def mock_email_data():
    """
    Sample email data for testing.
    
    Returns:
        dict: Mock email data structure
    """
    return {
        'data': {
            'id': '67890',
            'type': 'Email',
            'attributes': {
                'address': 'john.doe@example.com',
                'location': 'Work',
                'primary': True
            }
        }
    }


@pytest.fixture
def mock_campus_data():
    """
    Sample campus data for testing.
    
    Returns:
        dict: Mock campus data structure
    """
    return {
        'data': {
            'id': '1',
            'type': 'Campus',
            'attributes': {
                'name': 'Main Campus',
                'description': 'Primary campus location',
                'created_at': '2020-01-01T00:00:00Z'
            }
        }
    }


@pytest.fixture
def mock_person_list():
    """
    Sample list of people for testing pagination.
    
    Returns:
        list: List of mock person data
    """
    return [
        {
            'data': {
                'id': str(i),
                'type': 'Person',
                'attributes': {
                    'first_name': f'Person{i}',
                    'last_name': f'Test{i}',
                    'gender': 'Male' if i % 2 == 0 else 'Female',
                    'status': 'active',
                    'membership': 'Member'
                }
            }
        }
        for i in range(1, 6)
    ]


@pytest.fixture
def flask_test_client():
    """
    Create a Flask test client for API endpoint testing.
    
    Returns:
        FlaskClient: Flask test client
    """
    from src.app import app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_env_vars(monkeypatch):
    """
    Set up mock environment variables for testing.
    
    Args:
        monkeypatch: Pytest monkeypatch fixture
    """
    monkeypatch.setenv('PCO_APP_ID', 'test_app_id')
    monkeypatch.setenv('PCO_SECRET', 'test_secret')
    monkeypatch.setenv('FLASK_DEBUG', 'False')
    monkeypatch.setenv('FLASK_HOST', '0.0.0.0')
    monkeypatch.setenv('FLASK_PORT', '5000')


@pytest.fixture
def sample_person_attributes():
    """
    Sample person attributes for creating/updating people.
    
    Returns:
        dict: Person attributes
    """
    return {
        'first_name': 'Jane',
        'last_name': 'Smith',
        'gender': 'Female',
        'birthdate': '1985-05-15'
    }


@pytest.fixture
def mock_pco_response_with_included():
    """
    Mock PCO response with included data (emails, phone numbers).
    
    Returns:
        dict: Complete PCO response with relationships
    """
    return {
        'data': {
            'id': '12345',
            'type': 'Person',
            'attributes': {
                'first_name': 'John',
                'last_name': 'Doe',
                'gender': 'Male',
                'status': 'active'
            }
        },
        'included': [
            {
                'id': '1',
                'type': 'Email',
                'attributes': {
                    'address': 'john@example.com',
                    'location': 'Work'
                }
            },
            {
                'id': '2',
                'type': 'Email',
                'attributes': {
                    'address': 'john.personal@example.com',
                    'location': 'Home'
                }
            }
        ]
    }


@pytest.fixture(autouse=True)
def reset_environment():
    """
    Reset environment after each test to prevent side effects.
    """
    yield
    # Cleanup code here if needed


# Pytest hooks for custom behavior
def pytest_configure(config):
    """
    Configure pytest with custom settings.
    """
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )


def pytest_collection_modifyitems(config, items):
    """
    Modify test collection to add markers automatically.
    """
    for item in items:
        # Add unit marker to tests in unit directory
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        # Add integration marker to tests in integration directory
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        # Add performance marker to tests in performance directory
        elif "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)