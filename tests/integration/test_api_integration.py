"""
Integration tests for Flask API endpoints
These tests require the Flask app to be running and PCO credentials
Run with: pytest tests/integration/test_api_integration.py -m integration
"""

import pytest
import requests
import json
import time


# Skip all integration tests if not explicitly enabled
pytestmark = pytest.mark.integration


# API Base URL - adjust if needed
BASE_URL = "http://localhost:5000"


@pytest.fixture(scope="module")
def api_available():
    """
    Check if the API is available before running tests.
    """
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            pytest.skip("API is not available or not healthy")
    except requests.exceptions.RequestException:
        pytest.skip("API server is not running. Start with: python src/app.py")


@pytest.fixture(scope="module")
def test_person_data():
    """
    Create test person data and clean up after tests.
    """
    person_id = None
    
    # Create test person
    payload = {
        "first_name": "APITest",
        "last_name": "Integration",
        "gender": "Male"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/people",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            data = response.json()
            person_id = data.get('id')
    except:
        pass
    
    yield person_id
    
    # Cleanup
    if person_id:
        try:
            requests.delete(f"{BASE_URL}/api/people/{person_id}")
            print(f"\nCleaned up test person: {person_id}")
        except:
            pass


class TestHealthEndpoint:
    """Integration tests for health endpoint"""
    
    def test_health_check(self, api_available):
        """Test health check endpoint"""
        response = requests.get(f"{BASE_URL}/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert 'service' in data
        assert 'version' in data


class TestPeopleEndpoints:
    """Integration tests for people endpoints"""
    
    def test_get_all_people(self, api_available):
        """Test getting all people"""
        response = requests.get(f"{BASE_URL}/api/people")
        
        assert response.status_code == 200
        data = response.json()
        assert 'count' in data
        assert 'data' in data
        assert isinstance(data['data'], list)
    
    def test_get_people_with_filters(self, api_available):
        """Test getting people with filters"""
        response = requests.get(f"{BASE_URL}/api/people?role=member&status=active")
        
        assert response.status_code == 200
        data = response.json()
        assert data['filters']['role'] == 'member'
        assert data['filters']['status'] == 'active'
    
    def test_get_people_text_format(self, api_available):
        """Test getting people in text format"""
        response = requests.get(f"{BASE_URL}/api/people?format=text")
        
        assert response.status_code == 200
        data = response.json()
        assert 'context' in data
        assert isinstance(data['context'], str)
    
    def test_create_person(self, api_available):
        """Test creating a new person"""
        payload = {
            "first_name": "TestCreate",
            "last_name": "Person",
            "gender": "Female"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/people",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert 'id' in data
        assert data['message'] == 'Person created successfully'
        
        # Cleanup
        person_id = data['id']
        requests.delete(f"{BASE_URL}/api/people/{person_id}")
    
    def test_create_person_missing_fields(self, api_available):
        """Test creating person with missing required fields"""
        payload = {
            "first_name": "TestMissing"
            # Missing last_name
        }
        
        response = requests.post(
            f"{BASE_URL}/api/people",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert 'error' in data
    
    def test_get_person_by_id(self, api_available, test_person_data):
        """Test getting a specific person by ID"""
        if not test_person_data:
            pytest.skip("Test person not available")
        
        response = requests.get(f"{BASE_URL}/api/people/{test_person_data}")
        
        assert response.status_code == 200
        data = response.json()
        assert data['id'] == test_person_data
        assert 'first_name' in data
        assert 'last_name' in data
    
    def test_get_nonexistent_person(self, api_available):
        """Test getting a person that doesn't exist"""
        response = requests.get(f"{BASE_URL}/api/people/99999999")
        
        assert response.status_code in [404, 500]
    
    def test_update_person(self, api_available, test_person_data):
        """Test updating a person"""
        if not test_person_data:
            pytest.skip("Test person not available")
        
        payload = {
            "gender": "Female"
        }
        
        response = requests.patch(
            f"{BASE_URL}/api/people/{test_person_data}",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['message'] == 'Person updated successfully'
        assert data['id'] == test_person_data
    
    def test_update_person_no_data(self, api_available, test_person_data):
        """Test updating person with no data"""
        if not test_person_data:
            pytest.skip("Test person not available")
        
        response = requests.patch(
            f"{BASE_URL}/api/people/{test_person_data}",
            json={},
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 400
    
    def test_delete_person(self, api_available):
        """Test deleting a person"""
        # Create a person to delete
        payload = {
            "first_name": "TestDelete",
            "last_name": "Person",
            "gender": "Male"
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/people",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if create_response.status_code != 201:
            pytest.skip("Could not create test person")
        
        person_id = create_response.json()['id']
        
        # Delete the person
        response = requests.delete(f"{BASE_URL}/api/people/{person_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data['message'] == 'Person deleted successfully'
        assert data['id'] == person_id


class TestCampusesEndpoint:
    """Integration tests for campuses endpoint"""
    
    def test_get_all_campuses(self, api_available):
        """Test getting all campuses"""
        response = requests.get(f"{BASE_URL}/api/campuses")
        
        assert response.status_code == 200
        data = response.json()
        assert 'count' in data
        assert 'data' in data
        assert isinstance(data['data'], list)


class TestCompleteWorkflow:
    """Integration tests for complete workflows"""
    
    def test_complete_crud_workflow(self, api_available):
        """Test complete CRUD workflow"""
        person_id = None
        
        try:
            # 1. Create person
            create_payload = {
                "first_name": "Workflow",
                "last_name": "Test",
                "gender": "Male",
                "birthdate": "1990-01-01"
            }
            
            create_response = requests.post(
                f"{BASE_URL}/api/people",
                json=create_payload,
                headers={"Content-Type": "application/json"}
            )
            
            assert create_response.status_code == 201
            person_id = create_response.json()['id']
            
            # 2. Read person
            get_response = requests.get(f"{BASE_URL}/api/people/{person_id}")
            assert get_response.status_code == 200
            person_data = get_response.json()
            assert person_data['first_name'] == "Workflow"
            assert person_data['last_name'] == "Test"
            
            # 3. Update person
            update_payload = {
                "gender": "Female"
            }
            
            update_response = requests.patch(
                f"{BASE_URL}/api/people/{person_id}",
                json=update_payload,
                headers={"Content-Type": "application/json"}
            )
            
            assert update_response.status_code == 200
            
            # 4. Verify update
            verify_response = requests.get(f"{BASE_URL}/api/people/{person_id}")
            assert verify_response.status_code == 200
            updated_data = verify_response.json()
            assert updated_data['gender'] == "Female"
            
            # 5. Delete person
            delete_response = requests.delete(f"{BASE_URL}/api/people/{person_id}")
            assert delete_response.status_code == 200
            person_id = None  # Mark as deleted
            
        finally:
            # Cleanup
            if person_id:
                try:
                    requests.delete(f"{BASE_URL}/api/people/{person_id}")
                except:
                    pass


class TestErrorHandling:
    """Integration tests for error handling"""
    
    def test_invalid_endpoint(self, api_available):
        """Test accessing invalid endpoint"""
        response = requests.get(f"{BASE_URL}/api/invalid")
        assert response.status_code == 404
    
    def test_invalid_method(self, api_available):
        """Test using invalid HTTP method"""
        response = requests.post(f"{BASE_URL}/health")
        assert response.status_code == 405
    
    def test_invalid_json(self, api_available):
        """Test sending invalid JSON"""
        response = requests.post(
            f"{BASE_URL}/api/people",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [400, 500]


class TestRateLimiting:
    """Integration tests for rate limiting behavior"""
    
    @pytest.mark.slow
    def test_multiple_requests(self, api_available):
        """Test making multiple requests in succession"""
        # Make several requests
        responses = []
        for i in range(5):
            response = requests.get(f"{BASE_URL}/health")
            responses.append(response.status_code)
            time.sleep(0.1)  # Small delay between requests
        
        # All should succeed (pypco handles rate limiting)
        assert all(status == 200 for status in responses)


class TestDataConsistency:
    """Integration tests for data consistency"""
    
    def test_create_and_retrieve_consistency(self, api_available):
        """Test that created data can be retrieved correctly"""
        person_id = None
        
        try:
            # Create person with specific data
            payload = {
                "first_name": "Consistency",
                "last_name": "Test",
                "gender": "Female",
                "birthdate": "1995-06-15"
            }
            
            create_response = requests.post(
                f"{BASE_URL}/api/people",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            assert create_response.status_code == 201
            person_id = create_response.json()['id']
            
            # Retrieve and verify
            get_response = requests.get(f"{BASE_URL}/api/people/{person_id}")
            assert get_response.status_code == 200
            
            data = get_response.json()
            assert data['first_name'] == payload['first_name']
            assert data['last_name'] == payload['last_name']
            assert data['gender'] == payload['gender']
            assert data['birthdate'] == payload['birthdate']
            
        finally:
            if person_id:
                requests.delete(f"{BASE_URL}/api/people/{person_id}")