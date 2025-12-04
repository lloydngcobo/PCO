"""
Unit tests for Flask API endpoints in app.py
Tests all REST API endpoints with mocked PCO client
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from tests.fixtures.mock_responses import (
    MOCK_PERSON_RESPONSE,
    MOCK_PERSON_LIST,
    MOCK_CAMPUS_LIST,
    MOCK_PERSON_RESPONSE_WITH_EMAILS,
    create_mock_person
)


class TestHealthEndpoint:
    """Tests for /health endpoint"""
    
    def test_health_check_success(self, flask_test_client):
        """Test health check returns correct status"""
        # Act
        response = flask_test_client.get('/health')
        data = json.loads(response.data)
        
        # Assert
        assert response.status_code == 200
        assert data['status'] == 'healthy'
        assert data['service'] == 'PCO API Wrapper'
        assert 'version' in data


class TestGetPeopleEndpoint:
    """Tests for GET /api/people endpoint"""
    
    @patch('src.app.pco')
    def test_get_people_success(self, mock_pco, flask_test_client):
        """Test getting all people successfully"""
        # Arrange
        mock_pco.iterate.side_effect = [
            MOCK_CAMPUS_LIST,  # Campus data
            MOCK_PERSON_LIST   # People data
        ]
        
        # Act
        response = flask_test_client.get('/api/people')
        data = json.loads(response.data)
        
        # Assert
        assert response.status_code == 200
        assert 'count' in data
        assert 'data' in data
        assert isinstance(data['data'], list)
    
    @patch('src.app.pco')
    def test_get_people_with_role_filter(self, mock_pco, flask_test_client):
        """Test filtering people by role"""
        # Arrange
        mock_pco.iterate.side_effect = [
            MOCK_CAMPUS_LIST,
            MOCK_PERSON_LIST
        ]
        
        # Act
        response = flask_test_client.get('/api/people?role=member')
        data = json.loads(response.data)
        
        # Assert
        assert response.status_code == 200
        assert data['filters']['role'] == 'member'
    
    @patch('src.app.pco')
    def test_get_people_with_status_filter(self, mock_pco, flask_test_client):
        """Test filtering people by status"""
        # Arrange
        mock_pco.iterate.side_effect = [
            MOCK_CAMPUS_LIST,
            MOCK_PERSON_LIST
        ]
        
        # Act
        response = flask_test_client.get('/api/people?status=active')
        data = json.loads(response.data)
        
        # Assert
        assert response.status_code == 200
        assert data['filters']['status'] == 'active'
    
    @patch('src.app.pco')
    def test_get_people_with_campus_filter(self, mock_pco, flask_test_client):
        """Test filtering people by campus"""
        # Arrange
        mock_pco.iterate.side_effect = [
            MOCK_CAMPUS_LIST,
            MOCK_PERSON_LIST
        ]
        
        # Act
        response = flask_test_client.get('/api/people?campus_id=1')
        data = json.loads(response.data)
        
        # Assert
        assert response.status_code == 200
        assert data['filters']['campus_id'] == '1'
    
    @patch('src.app.pco')
    def test_get_people_text_format(self, mock_pco, flask_test_client):
        """Test getting people in text format"""
        # Arrange
        mock_pco.iterate.side_effect = [
            MOCK_CAMPUS_LIST,
            MOCK_PERSON_LIST
        ]
        
        # Act
        response = flask_test_client.get('/api/people?format=text')
        data = json.loads(response.data)
        
        # Assert
        assert response.status_code == 200
        assert 'context' in data
        assert isinstance(data['context'], str)
    
    @patch('src.app.pco')
    def test_get_people_api_error(self, mock_pco, flask_test_client):
        """Test handling of API errors"""
        # Arrange
        mock_pco.iterate.side_effect = Exception("API Error")
        
        # Act
        response = flask_test_client.get('/api/people')
        data = json.loads(response.data)
        
        # Assert
        assert response.status_code == 500
        assert 'error' in data


class TestGetPersonByIdEndpoint:
    """Tests for GET /api/people/<person_id> endpoint"""
    
    @patch('src.app.pco')
    def test_get_person_by_id_success(self, mock_pco, flask_test_client):
        """Test getting a specific person by ID"""
        # Arrange
        mock_pco.get.return_value = MOCK_PERSON_RESPONSE_WITH_EMAILS
        
        # Act
        response = flask_test_client.get('/api/people/12345')
        data = json.loads(response.data)
        
        # Assert
        assert response.status_code == 200
        assert data['id'] == '12345'
        assert data['first_name'] == 'John'
        assert data['last_name'] == 'Doe'
        assert 'emails' in data
    
    @patch('src.app.pco')
    def test_get_person_by_id_not_found(self, mock_pco, flask_test_client):
        """Test when person is not found"""
        # Arrange
        mock_pco.get.return_value = None
        
        # Act
        response = flask_test_client.get('/api/people/99999')
        data = json.loads(response.data)
        
        # Assert
        assert response.status_code == 404
        assert 'error' in data
        assert data['error'] == 'Person not found'
    
    @patch('src.app.pco')
    def test_get_person_by_id_api_error(self, mock_pco, flask_test_client):
        """Test handling of API errors"""
        # Arrange
        mock_pco.get.side_effect = Exception("API Error")
        
        # Act
        response = flask_test_client.get('/api/people/12345')
        data = json.loads(response.data)
        
        # Assert
        assert response.status_code == 500
        assert 'error' in data


class TestCreatePersonEndpoint:
    """Tests for POST /api/people endpoint"""
    
    @patch('src.app.pco')
    def test_create_person_success(self, mock_pco, flask_test_client):
        """Test successfully creating a new person"""
        # Arrange
        mock_pco.template.return_value = {'data': {'type': 'Person'}}
        mock_pco.post.return_value = MOCK_PERSON_RESPONSE
        
        payload = {
            'first_name': 'John',
            'last_name': 'Doe',
            'gender': 'Male',
            'birthdate': '1990-01-01'
        }
        
        # Act
        response = flask_test_client.post(
            '/api/people',
            data=json.dumps(payload),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        # Assert
        assert response.status_code == 201
        assert data['message'] == 'Person created successfully'
        assert data['id'] == '12345'
        assert 'data' in data
    
    @patch('src.app.pco')
    def test_create_person_minimal_data(self, mock_pco, flask_test_client):
        """Test creating person with only required fields"""
        # Arrange
        mock_pco.template.return_value = {'data': {'type': 'Person'}}
        mock_pco.post.return_value = MOCK_PERSON_RESPONSE
        
        payload = {
            'first_name': 'John',
            'last_name': 'Doe'
        }
        
        # Act
        response = flask_test_client.post(
            '/api/people',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 201
    
    def test_create_person_missing_first_name(self, flask_test_client):
        """Test error when first_name is missing"""
        # Arrange
        payload = {
            'last_name': 'Doe'
        }
        
        # Act
        response = flask_test_client.post(
            '/api/people',
            data=json.dumps(payload),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        # Assert
        assert response.status_code == 400
        assert 'error' in data
        assert 'first_name' in data['error']
    
    def test_create_person_missing_last_name(self, flask_test_client):
        """Test error when last_name is missing"""
        # Arrange
        payload = {
            'first_name': 'John'
        }
        
        # Act
        response = flask_test_client.post(
            '/api/people',
            data=json.dumps(payload),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        # Assert
        assert response.status_code == 400
        assert 'error' in data
        assert 'last_name' in data['error']
    
    def test_create_person_no_data(self, flask_test_client):
        """Test error when no data is provided"""
        # Act
        response = flask_test_client.post(
            '/api/people',
            data=json.dumps({}),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        # Assert
        assert response.status_code == 400
        assert 'error' in data
    
    @patch('src.app.pco')
    def test_create_person_api_error(self, mock_pco, flask_test_client):
        """Test handling of API errors during creation"""
        # Arrange
        mock_pco.template.return_value = {'data': {'type': 'Person'}}
        mock_pco.post.side_effect = Exception("API Error")
        
        payload = {
            'first_name': 'John',
            'last_name': 'Doe'
        }
        
        # Act
        response = flask_test_client.post(
            '/api/people',
            data=json.dumps(payload),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        # Assert
        assert response.status_code == 500
        assert 'error' in data


class TestUpdatePersonEndpoint:
    """Tests for PATCH /api/people/<person_id> endpoint"""
    
    @patch('src.app.pco')
    def test_update_person_success(self, mock_pco, flask_test_client):
        """Test successfully updating a person"""
        # Arrange
        mock_pco.template.return_value = {'data': {'type': 'Person'}}
        mock_pco.patch.return_value = MOCK_PERSON_RESPONSE
        
        payload = {
            'gender': 'Female',
            'birthdate': '1990-01-01'
        }
        
        # Act
        response = flask_test_client.patch(
            '/api/people/12345',
            data=json.dumps(payload),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        # Assert
        assert response.status_code == 200
        assert data['message'] == 'Person updated successfully'
        assert data['id'] == '12345'
    
    @patch('src.app.pco')
    def test_update_person_single_field(self, mock_pco, flask_test_client):
        """Test updating a single field"""
        # Arrange
        mock_pco.template.return_value = {'data': {'type': 'Person'}}
        mock_pco.patch.return_value = MOCK_PERSON_RESPONSE
        
        payload = {'gender': 'Female'}
        
        # Act
        response = flask_test_client.patch(
            '/api/people/12345',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 200
    
    def test_update_person_no_data(self, flask_test_client):
        """Test error when no data is provided"""
        # Act
        response = flask_test_client.patch(
            '/api/people/12345',
            data=json.dumps({}),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        # Assert
        assert response.status_code == 400
        assert 'error' in data
    
    @patch('src.app.pco')
    def test_update_person_api_error(self, mock_pco, flask_test_client):
        """Test handling of API errors during update"""
        # Arrange
        mock_pco.template.return_value = {'data': {'type': 'Person'}}
        mock_pco.patch.side_effect = Exception("API Error")
        
        payload = {'gender': 'Female'}
        
        # Act
        response = flask_test_client.patch(
            '/api/people/12345',
            data=json.dumps(payload),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        # Assert
        assert response.status_code == 500
        assert 'error' in data


class TestDeletePersonEndpoint:
    """Tests for DELETE /api/people/<person_id> endpoint"""
    
    @patch('src.app.pco')
    def test_delete_person_success(self, mock_pco, flask_test_client):
        """Test successfully deleting a person"""
        # Arrange
        mock_pco.delete.return_value = None
        
        # Act
        response = flask_test_client.delete('/api/people/12345')
        data = json.loads(response.data)
        
        # Assert
        assert response.status_code == 200
        assert data['message'] == 'Person deleted successfully'
        assert data['id'] == '12345'
    
    @patch('src.app.pco')
    def test_delete_person_api_error(self, mock_pco, flask_test_client):
        """Test handling of API errors during deletion"""
        # Arrange
        mock_pco.delete.side_effect = Exception("API Error")
        
        # Act
        response = flask_test_client.delete('/api/people/12345')
        data = json.loads(response.data)
        
        # Assert
        assert response.status_code == 500
        assert 'error' in data


class TestGetCampusesEndpoint:
    """Tests for GET /api/campuses endpoint"""
    
    @patch('src.app.pco')
    def test_get_campuses_success(self, mock_pco, flask_test_client):
        """Test getting all campuses successfully"""
        # Arrange
        mock_pco.iterate.return_value = MOCK_CAMPUS_LIST
        
        # Act
        response = flask_test_client.get('/api/campuses')
        data = json.loads(response.data)
        
        # Assert
        assert response.status_code == 200
        assert 'count' in data
        assert 'data' in data
        assert data['count'] == 2
        assert len(data['data']) == 2
    
    @patch('src.app.pco')
    def test_get_campuses_empty(self, mock_pco, flask_test_client):
        """Test when no campuses exist"""
        # Arrange
        mock_pco.iterate.return_value = []
        
        # Act
        response = flask_test_client.get('/api/campuses')
        data = json.loads(response.data)
        
        # Assert
        assert response.status_code == 200
        assert data['count'] == 0
        assert data['data'] == []
    
    @patch('src.app.pco')
    def test_get_campuses_api_error(self, mock_pco, flask_test_client):
        """Test handling of API errors"""
        # Arrange
        mock_pco.iterate.side_effect = Exception("API Error")
        
        # Act
        response = flask_test_client.get('/api/campuses')
        data = json.loads(response.data)
        
        # Assert
        assert response.status_code == 500
        assert 'error' in data


class TestContentTypeHandling:
    """Tests for content type handling"""
    
    def test_post_without_content_type(self, flask_test_client):
        """Test POST request without content-type header"""
        # Act
        response = flask_test_client.post(
            '/api/people',
            data='{"first_name":"John","last_name":"Doe"}'
        )
        
        # Assert
        # Should still work or return appropriate error
        assert response.status_code in [201, 400, 415, 500]
    
    def test_post_with_invalid_json(self, flask_test_client):
        """Test POST request with invalid JSON"""
        # Act
        response = flask_test_client.post(
            '/api/people',
            data='invalid json',
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code in [400, 500]


class TestErrorResponses:
    """Tests for error response formats"""
    
    def test_404_endpoint(self, flask_test_client):
        """Test accessing non-existent endpoint"""
        # Act
        response = flask_test_client.get('/api/nonexistent')
        
        # Assert
        assert response.status_code == 404
    
    def test_method_not_allowed(self, flask_test_client):
        """Test using wrong HTTP method"""
        # Act
        response = flask_test_client.post('/health')
        
        # Assert
        assert response.status_code == 405