"""
Unit tests for services_helpers.py
Tests all Services module helper functions with mocked PCO API responses
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from services_helpers import (
    get_service_types,
    get_service_type_by_id,
    get_plans,
    get_plan_by_id,
    create_plan,
    update_plan,
    delete_plan,
    get_teams,
    get_team_by_id,
    get_team_positions,
    get_plan_people,
    add_person_to_plan,
    remove_person_from_plan,
    update_plan_person_status,
    get_upcoming_plans,
    get_past_plans,
    find_plan_by_date
)


class TestServiceTypes:
    """Tests for service type functions"""
    
    def test_get_service_types_success(self, mock_pco_client):
        """Test getting all service types"""
        # Mock response
        mock_service_types = [
            {
                'data': {
                    'id': '1',
                    'type': 'ServiceType',
                    'attributes': {
                        'name': 'Sunday Service',
                        'frequency': 'Weekly',
                        'sequence': 1,
                        'created_at': '2024-01-01T00:00:00Z',
                        'updated_at': '2024-01-01T00:00:00Z',
                        'archived_at': None
                    }
                }
            },
            {
                'data': {
                    'id': '2',
                    'type': 'ServiceType',
                    'attributes': {
                        'name': 'Wednesday Service',
                        'frequency': 'Weekly',
                        'sequence': 2,
                        'created_at': '2024-01-01T00:00:00Z',
                        'updated_at': '2024-01-01T00:00:00Z',
                        'archived_at': None
                    }
                }
            }
        ]
        
        mock_pco_client.iterate.return_value = mock_service_types
        
        # Call function
        result = get_service_types(mock_pco_client)
        
        # Assertions
        assert len(result) == 2
        assert result[0]['id'] == '1'
        assert result[0]['name'] == 'Sunday Service'
        assert result[1]['id'] == '2'
        assert result[1]['name'] == 'Wednesday Service'
        mock_pco_client.iterate.assert_called_once_with('/services/v2/service_types')
    
    def test_get_service_types_empty(self, mock_pco_client):
        """Test getting service types when none exist"""
        mock_pco_client.iterate.return_value = []
        
        result = get_service_types(mock_pco_client)
        
        assert result == []
    
    def test_get_service_types_error(self, mock_pco_client):
        """Test error handling when getting service types"""
        mock_pco_client.iterate.side_effect = Exception("API Error")
        
        # Function catches exceptions and returns empty list
        result = get_service_types(mock_pco_client)
        assert result == []
    
    def test_get_service_type_by_id_success(self, mock_pco_client):
        """Test getting a specific service type"""
        mock_response = {
            'data': {
                'id': '1',
                'type': 'ServiceType',
                'attributes': {
                    'name': 'Sunday Service',
                    'frequency': 'Weekly',
                    'sequence': 1,
                    'created_at': '2024-01-01T00:00:00Z',
                    'updated_at': '2024-01-01T00:00:00Z',
                    'archived_at': None
                }
            }
        }
        
        mock_pco_client.get.return_value = mock_response
        
        result = get_service_type_by_id(mock_pco_client, '1')
        
        assert result['id'] == '1'
        assert result['name'] == 'Sunday Service'
        mock_pco_client.get.assert_called_once_with('/services/v2/service_types/1')
    
    def test_get_service_type_by_id_not_found(self, mock_pco_client):
        """Test getting non-existent service type"""
        mock_pco_client.get.return_value = None
        
        result = get_service_type_by_id(mock_pco_client, '999')
        
        assert result is None


class TestPlans:
    """Tests for plan functions"""
    
    def test_get_plans_success(self, mock_pco_client):
        """Test getting plans for a service type"""
        mock_plans = [
            {
                'data': {
                    'id': '1',
                    'type': 'Plan',
                    'attributes': {
                        'title': 'Christmas Service',
                        'series_title': 'Christmas 2024',
                        'dates': '2024-12-25',
                        'sort_date': '2024-12-25T10:00:00Z',
                        'short_dates': 'Dec 25',
                        'planning_center_url': 'https://planning.center/plans/1',
                        'created_at': '2024-01-01T00:00:00Z',
                        'updated_at': '2024-01-01T00:00:00Z'
                    }
                }
            }
        ]
        
        mock_pco_client.iterate.return_value = mock_plans
        
        result = get_plans(mock_pco_client, '1')
        
        assert len(result) == 1
        assert result[0]['id'] == '1'
        assert result[0]['title'] == 'Christmas Service'
        mock_pco_client.iterate.assert_called_once()
    
    def test_get_plans_with_filters(self, mock_pco_client):
        """Test getting plans with filter and order parameters"""
        mock_pco_client.iterate.return_value = []
        
        get_plans(mock_pco_client, '1', filter_by='future', order='-sort_date')
        
        call_args = mock_pco_client.iterate.call_args
        assert call_args is not None
    
    def test_get_plan_by_id_success(self, mock_pco_client):
        """Test getting a specific plan"""
        mock_response = {
            'data': {
                'id': '1',
                'type': 'Plan',
                'attributes': {
                    'title': 'Christmas Service',
                    'series_title': 'Christmas 2024',
                    'dates': '2024-12-25',
                    'sort_date': '2024-12-25T10:00:00Z',
                    'short_dates': 'Dec 25',
                    'planning_center_url': 'https://planning.center/plans/1',
                    'created_at': '2024-01-01T00:00:00Z',
                    'updated_at': '2024-01-01T00:00:00Z'
                }
            }
        }
        
        mock_pco_client.get.return_value = mock_response
        
        result = get_plan_by_id(mock_pco_client, '1', '1')
        
        assert result['id'] == '1'
        assert result['title'] == 'Christmas Service'
    
    def test_create_plan_success(self, mock_pco_client):
        """Test creating a new plan"""
        mock_response = {
            'data': {
                'id': '123',
                'type': 'Plan',
                'attributes': {
                    'title': 'New Service',
                    'dates': '2024-12-31'
                }
            }
        }
        
        mock_pco_client.template.return_value = {'data': {'type': 'Plan'}}
        mock_pco_client.post.return_value = mock_response
        
        result = create_plan(
            mock_pco_client,
            '1',
            title='New Service',
            dates='2024-12-31',
            series_title='End of Year'
        )
        
        assert result['id'] == '123'
        assert result['title'] == 'New Service'
        mock_pco_client.template.assert_called_once()
        mock_pco_client.post.assert_called_once()
    
    def test_create_plan_minimal(self, mock_pco_client):
        """Test creating plan with minimal fields"""
        mock_response = {
            'data': {
                'id': '123',
                'type': 'Plan',
                'attributes': {
                    'title': 'New Service'
                }
            }
        }
        
        mock_pco_client.template.return_value = {'data': {'type': 'Plan'}}
        mock_pco_client.post.return_value = mock_response
        
        result = create_plan(mock_pco_client, '1', title='New Service')
        
        assert result['id'] == '123'
    
    def test_update_plan_success(self, mock_pco_client):
        """Test updating a plan"""
        mock_response = {
            'data': {
                'id': '1',
                'type': 'Plan',
                'attributes': {
                    'title': 'Updated Service',
                    'dates': '2024-12-31',
                    'created_at': '2024-01-01T00:00:00Z',
                    'updated_at': '2024-01-02T00:00:00Z'
                }
            }
        }
        
        mock_pco_client.template.return_value = {'data': {'type': 'Plan'}}
        mock_pco_client.patch.return_value = mock_response
        
        result = update_plan(mock_pco_client, '1', '1', {'title': 'Updated Service'})
        
        assert result['id'] == '1'
        assert result['data']['attributes']['title'] == 'Updated Service'
        mock_pco_client.patch.assert_called_once()
    
    def test_delete_plan_success(self, mock_pco_client):
        """Test deleting a plan"""
        mock_pco_client.delete.return_value = None
        
        result = delete_plan(mock_pco_client, '1', '1')
        
        assert result is True
        mock_pco_client.delete.assert_called_once_with('/services/v2/service_types/1/plans/1')


class TestTeams:
    """Tests for team functions"""
    
    def test_get_teams_success(self, mock_pco_client):
        """Test getting teams for a service type"""
        mock_teams = [
            {
                'data': {
                    'id': '1',
                    'type': 'Team',
                    'attributes': {
                        'name': 'Worship Team',
                        'sequence': 1,
                        'schedule_to': 'plan',
                        'default_status': 'C',
                        'created_at': '2024-01-01T00:00:00Z',
                        'updated_at': '2024-01-01T00:00:00Z'
                    }
                }
            }
        ]
        
        mock_pco_client.iterate.return_value = mock_teams
        
        result = get_teams(mock_pco_client, '1')
        
        assert len(result) == 1
        assert result[0]['name'] == 'Worship Team'
    
    def test_get_team_by_id_success(self, mock_pco_client):
        """Test getting a specific team"""
        mock_response = {
            'data': {
                'id': '1',
                'type': 'Team',
                'attributes': {
                    'name': 'Worship Team',
                    'sequence': 1,
                    'schedule_to': 'plan',
                    'default_status': 'C',
                    'created_at': '2024-01-01T00:00:00Z',
                    'updated_at': '2024-01-01T00:00:00Z'
                }
            }
        }
        
        mock_pco_client.get.return_value = mock_response
        
        result = get_team_by_id(mock_pco_client, '1', '1')
        
        assert result['name'] == 'Worship Team'
    
    def test_get_team_positions_success(self, mock_pco_client):
        """Test getting positions for a team"""
        mock_positions = [
            {
                'data': {
                    'id': '1',
                    'type': 'TeamPosition',
                    'attributes': {
                        'name': 'Vocalist',
                        'created_at': '2024-01-01T00:00:00Z',
                        'updated_at': '2024-01-01T00:00:00Z'
                    }
                }
            }
        ]
        
        mock_pco_client.iterate.return_value = mock_positions
        
        result = get_team_positions(mock_pco_client, '1', '1')
        
        assert len(result) == 1
        assert result[0]['name'] == 'Vocalist'


class TestPlanPeople:
    """Tests for plan people functions"""
    
    def test_get_plan_people_success(self, mock_pco_client):
        """Test getting people assigned to a plan"""
        mock_people = [
            {
                'data': {
                    'id': '1',
                    'type': 'TeamMember',
                    'attributes': {
                        'status': 'C',
                        'team_position_name': 'Vocalist',
                        'scheduled_by_name': 'Admin',
                        'created_at': '2024-01-01T00:00:00Z',
                        'updated_at': '2024-01-01T00:00:00Z'
                    }
                },
                'included': [
                    {
                        'type': 'Person',
                        'attributes': {
                            'full_name': 'John Doe'
                        }
                    },
                    {
                        'type': 'Team',
                        'attributes': {
                            'name': 'Worship Team'
                        }
                    }
                ]
            }
        ]
        
        mock_pco_client.iterate.return_value = mock_people
        
        result = get_plan_people(mock_pco_client, '1', '1')
        
        assert len(result) == 1
        assert result[0]['person_name'] == 'John Doe'
        assert result[0]['status'] == 'C'
    
    def test_add_person_to_plan_success(self, mock_pco_client):
        """Test adding a person to a plan"""
        mock_response = {
            'data': {
                'id': '123',
                'type': 'TeamMember',
                'attributes': {
                    'status': 'C'
                }
            }
        }
        
        mock_pco_client.post.return_value = mock_response
        
        result = add_person_to_plan(
            mock_pco_client,
            '1',
            '1',
            person_id='456',
            team_id='111',
            team_position_id='789',
            status='C'
        )
        
        assert result['id'] == '123'
        mock_pco_client.post.assert_called_once()
    
    def test_add_person_to_plan_missing_fields(self, mock_pco_client):
        """Test adding person without required fields"""
        # Should handle missing required parameters
        mock_pco_client.post.side_effect = Exception("Missing required fields")
        
        result = add_person_to_plan(
            mock_pco_client, '1', '1',
            person_id='456', team_id='111', team_position_id='789'
        )
        
        # Function should return None on error
        assert result is None
    
    def test_remove_person_from_plan_success(self, mock_pco_client):
        """Test removing a person from a plan"""
        mock_pco_client.delete.return_value = None
        
        result = remove_person_from_plan(mock_pco_client, '1', '1', '123')
        
        assert result is True
        mock_pco_client.delete.assert_called_once()
    
    def test_update_plan_person_success(self, mock_pco_client):
        """Test updating a plan person's status"""
        mock_response = {
            'data': {
                'id': '123',
                'type': 'TeamMember',
                'attributes': {
                    'status': 'C'
                }
            }
        }
        
        mock_pco_client.template.return_value = {'data': {'type': 'TeamMember'}}
        mock_pco_client.patch.return_value = mock_response
        
        result = update_plan_person_status(mock_pco_client, '1', '1', '123', 'C')
        
        assert result['id'] == '123'
        mock_pco_client.patch.assert_called_once()


class TestPlanUtilities:
    """Tests for plan utility functions"""
    
    def test_get_upcoming_plans_success(self, mock_pco_client):
        """Test getting upcoming plans"""
        future_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        
        mock_plans = [
            {
                'data': {
                    'id': '1',
                    'type': 'Plan',
                    'attributes': {
                        'title': 'Future Service',
                        'series_title': 'Future Series',
                        'dates': future_date,
                        'sort_date': f'{future_date}T10:00:00Z',
                        'short_dates': 'Future',
                        'planning_center_url': 'https://planning.center/plans/1',
                        'created_at': '2024-01-01T00:00:00Z',
                        'updated_at': '2024-01-01T00:00:00Z'
                    }
                }
            }
        ]
        
        mock_pco_client.iterate.return_value = mock_plans
        
        result = get_upcoming_plans(mock_pco_client, '1', days_ahead=30)
        
        assert len(result) == 1
        assert result[0]['title'] == 'Future Service'
    
    def test_get_past_plans_success(self, mock_pco_client):
        """Test getting past plans"""
        past_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        mock_plans = [
            {
                'data': {
                    'id': '1',
                    'type': 'Plan',
                    'attributes': {
                        'title': 'Past Service',
                        'series_title': 'Past Series',
                        'dates': past_date,
                        'sort_date': f'{past_date}T10:00:00Z',
                        'short_dates': 'Past',
                        'planning_center_url': 'https://planning.center/plans/1',
                        'created_at': '2024-01-01T00:00:00Z',
                        'updated_at': '2024-01-01T00:00:00Z'
                    }
                }
            }
        ]
        
        mock_pco_client.iterate.return_value = mock_plans
        
        result = get_past_plans(mock_pco_client, '1', days_back=30)
        
        assert len(result) == 1
        assert result[0]['title'] == 'Past Service'
    
    def test_find_plan_by_date_success(self, mock_pco_client):
        """Test finding a plan by specific date"""
        target_date = '2024-06-15'
        
        mock_plans = [
            {
                'data': {
                    'id': '1',
                    'type': 'Plan',
                    'attributes': {
                        'title': 'Service on Date',
                        'series_title': 'June Series',
                        'dates': target_date,
                        'sort_date': f'{target_date}T10:00:00Z',
                        'short_dates': 'Jun 15',
                        'planning_center_url': 'https://planning.center/plans/1',
                        'created_at': '2024-01-01T00:00:00Z',
                        'updated_at': '2024-01-01T00:00:00Z'
                    }
                }
            }
        ]
        
        mock_pco_client.iterate.return_value = mock_plans
        
        result = find_plan_by_date(mock_pco_client, '1', target_date)
        
        assert result is not None
        assert result['title'] == 'Service on Date'
    
    def test_find_plan_by_date_not_found(self, mock_pco_client):
        """Test finding a plan when date doesn't match"""
        target_date = '2024-06-15'
        
        mock_plans = [
            {
                'data': {
                    'id': '1',
                    'type': 'Plan',
                    'attributes': {
                        'title': 'Different Date',
                        'dates': '2024-07-15',
                        'sort_date': '2024-07-15T10:00:00Z'
                    }
                }
            }
        ]
        
        mock_pco_client.iterate.return_value = mock_plans
        
        result = find_plan_by_date(mock_pco_client, '1', target_date)
        
        assert result is None


class TestErrorHandling:
    """Tests for error handling across all functions"""
    
    def test_network_error_handling(self, mock_pco_client):
        """Test handling of network errors"""
        mock_pco_client.iterate.side_effect = ConnectionError("Network error")
        
        # Functions catch exceptions and return empty list
        result = get_service_types(mock_pco_client)
        assert result == []
    
    def test_api_error_handling(self, mock_pco_client):
        """Test handling of API errors"""
        mock_pco_client.get.side_effect = Exception("API returned 500")
        
        # Functions catch exceptions and return None
        result = get_service_type_by_id(mock_pco_client, '1')
        assert result is None
    
    def test_invalid_data_handling(self, mock_pco_client):
        """Test handling of invalid data"""
        mock_pco_client.iterate.return_value = [
            {'data': {'id': '1', 'attributes': {}}}  # Missing required attributes
        ]
        
        # Should handle gracefully and return empty list due to KeyError
        result = get_service_types(mock_pco_client)
        assert result == []