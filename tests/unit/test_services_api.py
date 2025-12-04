"""
Unit tests for services_api.py
Tests all Services API Flask endpoints
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from services_api import services_bp
from flask import Flask


@pytest.fixture
def app():
    """Create Flask app for testing"""
    app = Flask(__name__)
    app.register_blueprint(services_bp, url_prefix='/api/services')
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def mock_pco():
    """Mock PCO client"""
    with patch('services_api.pco') as mock:
        yield mock


class TestServiceTypesEndpoints:
    """Tests for service types endpoints"""
    
    def test_get_service_types_success(self, client, mock_pco):
        """Test getting all service types"""
        with patch('services_api.get_service_types') as mock_get:
            mock_get.return_value = [
                {'id': '1', 'name': 'Sunday Service'},
                {'id': '2', 'name': 'Wednesday Service'}
            ]
            
            response = client.get('/api/services/service-types')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['count'] == 2
            assert len(data['data']) == 2
    
    def test_get_service_types_empty(self, client, mock_pco):
        """Test getting service types when none exist"""
        with patch('services_api.get_service_types') as mock_get:
            mock_get.return_value = []
            
            response = client.get('/api/services/service-types')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['count'] == 0
    
    def test_get_service_type_by_id_success(self, client, mock_pco):
        """Test getting a specific service type"""
        with patch('services_api.get_service_type_by_id') as mock_get:
            mock_get.return_value = {'id': '1', 'name': 'Sunday Service'}
            
            response = client.get('/api/services/service-types/1')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['id'] == '1'
    
    def test_get_service_type_by_id_not_found(self, client, mock_pco):
        """Test getting non-existent service type"""
        with patch('services_api.get_service_type_by_id') as mock_get:
            mock_get.return_value = None
            
            response = client.get('/api/services/service-types/999')
            
            assert response.status_code == 404


class TestPlansEndpoints:
    """Tests for plans endpoints"""
    
    def test_get_plans_success(self, client, mock_pco):
        """Test getting plans for a service type"""
        with patch('services_api.get_plans') as mock_get:
            mock_get.return_value = [
                {'id': '1', 'title': 'Christmas Service'}
            ]
            
            response = client.get('/api/services/service-types/1/plans')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['count'] == 1
    
    def test_get_plans_with_filters(self, client, mock_pco):
        """Test getting plans with filters"""
        with patch('services_api.get_plans') as mock_get:
            mock_get.return_value = []
            
            response = client.get('/api/services/service-types/1/plans?filter=future&order=-sort_date')
            
            assert response.status_code == 200
            mock_get.assert_called_once()
    
    def test_get_plan_by_id_success(self, client, mock_pco):
        """Test getting a specific plan"""
        with patch('services_api.get_plan_by_id') as mock_get:
            mock_get.return_value = {'id': '1', 'title': 'Christmas Service'}
            
            response = client.get('/api/services/service-types/1/plans/1')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['title'] == 'Christmas Service'
    
    def test_create_plan_success(self, client, mock_pco):
        """Test creating a new plan"""
        with patch('services_api.create_plan') as mock_create:
            mock_create.return_value = {'id': '123', 'title': 'New Service'}
            
            response = client.post('/api/services/service-types/1/plans',
                                  json={'title': 'New Service', 'dates': '2024-12-31'})
            
            assert response.status_code == 201
            data = response.get_json()
            assert data['message'] == 'Plan created successfully'
            assert data['data']['id'] == '123'
    
    def test_create_plan_missing_title(self, client, mock_pco):
        """Test creating plan without title"""
        response = client.post('/api/services/service-types/1/plans',
                              json={'dates': '2024-12-31'})
        
        assert response.status_code == 400
    
    def test_update_plan_success(self, client, mock_pco):
        """Test updating a plan"""
        with patch('services_api.update_plan') as mock_update:
            mock_update.return_value = {'id': '1', 'data': {'attributes': {'title': 'Updated'}}}
            
            response = client.patch('/api/services/service-types/1/plans/1',
                                   json={'title': 'Updated'})
            
            assert response.status_code == 200
    
    def test_delete_plan_success(self, client, mock_pco):
        """Test deleting a plan"""
        with patch('services_api.delete_plan') as mock_delete:
            mock_delete.return_value = True
            
            response = client.delete('/api/services/service-types/1/plans/1')
            
            assert response.status_code == 200


class TestTeamsEndpoints:
    """Tests for teams endpoints"""
    
    def test_get_teams_success(self, client, mock_pco):
        """Test getting teams"""
        with patch('services_api.get_teams') as mock_get:
            mock_get.return_value = [{'id': '1', 'name': 'Worship Team'}]
            
            response = client.get('/api/services/service-types/1/teams')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['count'] == 1
    
    def test_get_team_by_id_success(self, client, mock_pco):
        """Test getting a specific team"""
        with patch('services_api.get_team_by_id') as mock_get:
            mock_get.return_value = {'id': '1', 'name': 'Worship Team'}
            
            response = client.get('/api/services/service-types/1/teams/1')
            
            assert response.status_code == 200
    
    def test_get_team_positions_success(self, client, mock_pco):
        """Test getting team positions"""
        with patch('services_api.get_team_positions') as mock_get:
            mock_get.return_value = [{'id': '1', 'name': 'Vocalist'}]
            
            response = client.get('/api/services/service-types/1/teams/1/positions')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['count'] == 1


class TestPlanPeopleEndpoints:
    """Tests for plan people endpoints"""
    
    def test_get_plan_people_success(self, client, mock_pco):
        """Test getting people assigned to a plan"""
        with patch('services_api.get_plan_people') as mock_get:
            mock_get.return_value = [{'id': '1', 'person_name': 'John Doe'}]
            
            response = client.get('/api/services/service-types/1/plans/1/team-members')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['count'] == 1
    
    def test_add_person_to_plan_success(self, client, mock_pco):
        """Test adding a person to a plan"""
        with patch('services_api.add_person_to_plan') as mock_add:
            mock_add.return_value = {'id': '123'}
            
            response = client.post('/api/services/service-types/1/plans/1/team-members',
                                  json={'person_id': '456', 'team_id': '789', 'team_position_id': '101'})
            
            assert response.status_code == 201
    
    def test_add_person_missing_fields(self, client, mock_pco):
        """Test adding person without required fields"""
        response = client.post('/api/services/service-types/1/plans/1/team-members',
                              json={'person_id': '456'})
        
        assert response.status_code == 400
    
    def test_update_person_status_success(self, client, mock_pco):
        """Test updating person status"""
        with patch('services_api.update_plan_person_status') as mock_update:
            mock_update.return_value = {'id': '123'}
            
            response = client.patch('/api/services/service-types/1/plans/1/team-members/123',
                                   json={'status': 'C'})
            
            assert response.status_code == 200
    
    def test_remove_person_from_plan_success(self, client, mock_pco):
        """Test removing a person from a plan"""
        with patch('services_api.remove_person_from_plan') as mock_remove:
            mock_remove.return_value = True
            
            response = client.delete('/api/services/service-types/1/plans/1/team-members/123')
            
            assert response.status_code == 200


class TestUtilityEndpoints:
    """Tests for utility endpoints"""
    
    def test_get_upcoming_plans_success(self, client, mock_pco):
        """Test getting upcoming plans"""
        with patch('services_api.get_upcoming_plans') as mock_get:
            mock_get.return_value = [{'id': '1', 'title': 'Future Service'}]
            
            response = client.get('/api/services/service-types/1/plans/upcoming')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['count'] == 1
    
    def test_get_past_plans_success(self, client, mock_pco):
        """Test getting past plans"""
        with patch('services_api.get_past_plans') as mock_get:
            mock_get.return_value = [{'id': '1', 'title': 'Past Service'}]
            
            response = client.get('/api/services/service-types/1/plans/past')
            
            assert response.status_code == 200
    
    def test_find_plan_by_date_success(self, client, mock_pco):
        """Test finding a plan by date"""
        with patch('services_api.find_plan_by_date') as mock_find:
            mock_find.return_value = {'id': '1', 'title': 'Service on Date'}
            
            response = client.get('/api/services/service-types/1/plans/find-by-date?date=2024-06-15')
            
            assert response.status_code == 200
    
    def test_find_plan_by_date_not_found(self, client, mock_pco):
        """Test finding plan when date doesn't match"""
        with patch('services_api.find_plan_by_date') as mock_find:
            mock_find.return_value = None
            
            response = client.get('/api/services/service-types/1/plans/by-date/2024-06-15')
            
            assert response.status_code == 404


class TestErrorHandling:
    """Tests for error handling"""
    
    def test_service_type_error(self, client, mock_pco):
        """Test error handling for service types"""
        with patch('services_api.get_service_types') as mock_get:
            mock_get.side_effect = Exception("API Error")
            
            response = client.get('/api/services/service-types')
            
            assert response.status_code == 500
    
    def test_plan_error(self, client, mock_pco):
        """Test error handling for plans"""
        with patch('services_api.get_plans') as mock_get:
            mock_get.side_effect = Exception("API Error")
            
            response = client.get('/api/services/service-types/1/plans')
            
            assert response.status_code == 500