"""
Unit tests for pco_helpers.py
Tests all helper functions with mocked PCO client
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.pco_helpers import (
    get_pco_client,
    find_person_by_name,
    add_person,
    update_person_attribute,
    update_person_attributes,
    add_email_to_person,
    update_email,
    get_person_emails,
    delete_email,
    create_or_update_person,
    delete_person,
    get_person_by_id
)
from tests.fixtures.mock_responses import (
    MOCK_PERSON_RESPONSE,
    MOCK_EMAIL_RESPONSE,
    MOCK_EMAIL_LIST,
    create_mock_person,
    create_mock_email
)


class TestGetPCOClient:
    """Tests for get_pco_client function"""
    
    @patch('src.pco_helpers.pypco.PCO')
    @patch.dict('os.environ', {'PCO_APP_ID': 'test_id', 'PCO_SECRET': 'test_secret'})
    def test_get_pco_client_success(self, mock_pco_class):
        """Test successful PCO client initialization"""
        # Arrange
        mock_client = Mock()
        mock_pco_class.return_value = mock_client
        
        # Act
        client = get_pco_client()
        
        # Assert
        assert client is not None
        mock_pco_class.assert_called_once_with('test_id', 'test_secret')
    
    @patch.dict('os.environ', {}, clear=True)
    def test_get_pco_client_missing_credentials(self):
        """Test error when credentials are missing"""
        # Act & Assert
        with pytest.raises(ValueError, match="PCO_APP_ID and PCO_SECRET must be set"):
            get_pco_client()


class TestFindPersonByName:
    """Tests for find_person_by_name function"""
    
    def test_find_person_by_name_found(self, mock_pco_client):
        """Test finding a person that exists"""
        # Arrange
        mock_pco_client.iterate.return_value = [MOCK_PERSON_RESPONSE]
        
        # Act
        result = find_person_by_name(mock_pco_client, "John", "Doe")
        
        # Assert
        assert result is not None
        assert result['id'] == '12345'
        assert result['attributes']['first_name'] == 'John'
        assert result['attributes']['last_name'] == 'Doe'
        mock_pco_client.iterate.assert_called_once_with('/people/v2/people')
    
    def test_find_person_by_name_not_found(self, mock_pco_client):
        """Test when person doesn't exist"""
        # Arrange
        mock_pco_client.iterate.return_value = [
            create_mock_person('1', 'Jane', 'Smith')
        ]
        
        # Act
        result = find_person_by_name(mock_pco_client, "John", "Doe")
        
        # Assert
        assert result is None
    
    def test_find_person_by_name_empty_list(self, mock_pco_client):
        """Test with empty person list"""
        # Arrange
        mock_pco_client.iterate.return_value = []
        
        # Act
        result = find_person_by_name(mock_pco_client, "John", "Doe")
        
        # Assert
        assert result is None
    
    def test_find_person_by_name_api_error(self, mock_pco_client):
        """Test handling of API errors"""
        # Arrange
        mock_pco_client.iterate.side_effect = Exception("API Error")
        
        # Act
        result = find_person_by_name(mock_pco_client, "John", "Doe")
        
        # Assert
        assert result is None


class TestAddPerson:
    """Tests for add_person function"""
    
    def test_add_person_success(self, mock_pco_client):
        """Test successfully adding a new person"""
        # Arrange
        mock_pco_client.iterate.return_value = []  # No duplicates
        mock_pco_client.template.return_value = {'data': {'type': 'Person'}}
        mock_pco_client.post.return_value = MOCK_PERSON_RESPONSE
        
        # Act
        result = add_person(mock_pco_client, "John", "Doe", "Male", "1990-01-01")
        
        # Assert
        assert result is not None
        assert result['id'] == '12345'
        assert result['attributes']['first_name'] == 'John'
        mock_pco_client.post.assert_called_once()
    
    def test_add_person_duplicate_check(self, mock_pco_client):
        """Test duplicate person detection"""
        # Arrange
        mock_pco_client.iterate.return_value = [MOCK_PERSON_RESPONSE]
        
        # Act
        result = add_person(mock_pco_client, "John", "Doe", check_duplicate=True)
        
        # Assert
        assert result is None
        mock_pco_client.post.assert_not_called()
    
    def test_add_person_skip_duplicate_check(self, mock_pco_client):
        """Test adding person without duplicate check"""
        # Arrange
        mock_pco_client.template.return_value = {'data': {'type': 'Person'}}
        mock_pco_client.post.return_value = MOCK_PERSON_RESPONSE
        
        # Act
        result = add_person(mock_pco_client, "John", "Doe", check_duplicate=False)
        
        # Assert
        assert result is not None
        mock_pco_client.iterate.assert_not_called()
    
    def test_add_person_minimal_data(self, mock_pco_client):
        """Test adding person with only required fields"""
        # Arrange
        mock_pco_client.iterate.return_value = []
        mock_pco_client.template.return_value = {'data': {'type': 'Person'}}
        mock_pco_client.post.return_value = MOCK_PERSON_RESPONSE
        
        # Act
        result = add_person(mock_pco_client, "John", "Doe")
        
        # Assert
        assert result is not None
        # Verify template was called with minimal attributes
        call_args = mock_pco_client.template.call_args[0]
        assert call_args[1]['first_name'] == 'John'
        assert call_args[1]['last_name'] == 'Doe'
        assert 'gender' not in call_args[1] or call_args[1].get('gender') is None
    
    def test_add_person_api_error(self, mock_pco_client):
        """Test handling of API errors during person creation"""
        # Arrange
        mock_pco_client.iterate.return_value = []
        mock_pco_client.template.return_value = {'data': {'type': 'Person'}}
        mock_pco_client.post.side_effect = Exception("API Error")
        
        # Act
        result = add_person(mock_pco_client, "John", "Doe")
        
        # Assert
        assert result is None


class TestUpdatePersonAttribute:
    """Tests for update_person_attribute function"""
    
    def test_update_person_attribute_success(self, mock_pco_client):
        """Test successfully updating a single attribute"""
        # Arrange
        mock_pco_client.template.return_value = {'data': {'type': 'Person'}}
        mock_pco_client.patch.return_value = MOCK_PERSON_RESPONSE
        
        # Act
        result = update_person_attribute(mock_pco_client, "12345", "gender", "Female")
        
        # Assert
        assert result is not None
        assert result['id'] == '12345'
        mock_pco_client.patch.assert_called_once()
    
    def test_update_person_attribute_api_error(self, mock_pco_client):
        """Test handling of API errors during update"""
        # Arrange
        mock_pco_client.template.return_value = {'data': {'type': 'Person'}}
        mock_pco_client.patch.side_effect = Exception("API Error")
        
        # Act
        result = update_person_attribute(mock_pco_client, "12345", "gender", "Female")
        
        # Assert
        assert result is None


class TestUpdatePersonAttributes:
    """Tests for update_person_attributes function"""
    
    def test_update_person_attributes_success(self, mock_pco_client):
        """Test successfully updating multiple attributes"""
        # Arrange
        mock_pco_client.template.return_value = {'data': {'type': 'Person'}}
        mock_pco_client.patch.return_value = MOCK_PERSON_RESPONSE
        attributes = {'gender': 'Female', 'birthdate': '1990-01-01'}
        
        # Act
        result = update_person_attributes(mock_pco_client, "12345", attributes)
        
        # Assert
        assert result is not None
        assert result['id'] == '12345'
        mock_pco_client.template.assert_called_once_with('Person', attributes)
    
    def test_update_person_attributes_empty_dict(self, mock_pco_client):
        """Test updating with empty attributes dictionary"""
        # Arrange
        mock_pco_client.template.return_value = {'data': {'type': 'Person'}}
        mock_pco_client.patch.return_value = MOCK_PERSON_RESPONSE
        
        # Act
        result = update_person_attributes(mock_pco_client, "12345", {})
        
        # Assert
        assert result is not None


class TestEmailOperations:
    """Tests for email-related functions"""
    
    def test_add_email_to_person_success(self, mock_pco_client):
        """Test successfully adding an email"""
        # Arrange
        mock_pco_client.post.return_value = MOCK_EMAIL_RESPONSE
        
        # Act
        result = add_email_to_person(mock_pco_client, "12345", "test@example.com", "Work")
        
        # Assert
        assert result is not None
        assert result['id'] == '67890'
        assert result['attributes']['address'] == 'john.doe@example.com'
        mock_pco_client.post.assert_called_once()
    
    def test_add_email_default_location(self, mock_pco_client):
        """Test adding email with default location"""
        # Arrange
        mock_pco_client.post.return_value = MOCK_EMAIL_RESPONSE
        
        # Act
        result = add_email_to_person(mock_pco_client, "12345", "test@example.com")
        
        # Assert
        assert result is not None
        # Verify default location was used
        call_args = mock_pco_client.post.call_args[0]
        assert call_args[1]['data']['attributes']['location'] == 'Work'
    
    def test_update_email_success(self, mock_pco_client):
        """Test successfully updating an email"""
        # Arrange
        mock_pco_client.patch.return_value = MOCK_EMAIL_RESPONSE
        
        # Act
        result = update_email(mock_pco_client, "12345", "67890", "new@example.com", "Home")
        
        # Assert
        assert result is not None
        mock_pco_client.patch.assert_called_once()
    
    def test_update_email_partial(self, mock_pco_client):
        """Test updating only email address"""
        # Arrange
        mock_pco_client.patch.return_value = MOCK_EMAIL_RESPONSE
        
        # Act
        result = update_email(mock_pco_client, "12345", "67890", email_address="new@example.com")
        
        # Assert
        assert result is not None
        call_args = mock_pco_client.patch.call_args[0]
        assert 'address' in call_args[1]['data']['attributes']
        assert 'location' not in call_args[1]['data']['attributes']
    
    def test_get_person_emails_success(self, mock_pco_client):
        """Test getting all emails for a person"""
        # Arrange
        mock_pco_client.iterate.return_value = MOCK_EMAIL_LIST
        
        # Act
        result = get_person_emails(mock_pco_client, "12345")
        
        # Assert
        assert len(result) == 2
        assert result[0]['address'] == 'work@example.com'
        assert result[1]['address'] == 'home@example.com'
    
    def test_get_person_emails_empty(self, mock_pco_client):
        """Test getting emails when person has none"""
        # Arrange
        mock_pco_client.iterate.return_value = []
        
        # Act
        result = get_person_emails(mock_pco_client, "12345")
        
        # Assert
        assert result == []
    
    def test_delete_email_success(self, mock_pco_client):
        """Test successfully deleting an email"""
        # Arrange
        mock_pco_client.delete.return_value = None
        
        # Act
        result = delete_email(mock_pco_client, "12345", "67890")
        
        # Assert
        assert result is True
        mock_pco_client.delete.assert_called_once_with('/people/v2/people/12345/emails/67890')
    
    def test_delete_email_api_error(self, mock_pco_client):
        """Test handling of API errors during email deletion"""
        # Arrange
        mock_pco_client.delete.side_effect = Exception("API Error")
        
        # Act
        result = delete_email(mock_pco_client, "12345", "67890")
        
        # Assert
        assert result is False


class TestCreateOrUpdatePerson:
    """Tests for create_or_update_person function"""
    
    def test_create_new_person(self, mock_pco_client):
        """Test creating a new person when they don't exist"""
        # Arrange
        mock_pco_client.iterate.return_value = []  # Person not found
        mock_pco_client.template.return_value = {'data': {'type': 'Person'}}
        mock_pco_client.post.return_value = MOCK_PERSON_RESPONSE
        
        # Act
        result = create_or_update_person(mock_pco_client, "John", "Doe", "Male")
        
        # Assert
        assert result is not None
        assert result['id'] == '12345'
        mock_pco_client.post.assert_called_once()
    
    def test_update_existing_person(self, mock_pco_client):
        """Test updating an existing person"""
        # Arrange
        existing_person = create_mock_person('12345', 'John', 'Doe', gender='Male')
        mock_pco_client.iterate.return_value = [existing_person]
        mock_pco_client.template.return_value = {'data': {'type': 'Person'}}
        mock_pco_client.patch.return_value = MOCK_PERSON_RESPONSE
        
        # Act
        result = create_or_update_person(mock_pco_client, "John", "Doe", "Female")
        
        # Assert
        assert result is not None
        mock_pco_client.patch.assert_called_once()
    
    def test_create_or_update_with_email(self, mock_pco_client):
        """Test creating person with email"""
        # Arrange
        mock_pco_client.iterate.side_effect = [[], []]  # Person not found, no emails
        mock_pco_client.template.return_value = {'data': {'type': 'Person'}}
        mock_pco_client.post.side_effect = [MOCK_PERSON_RESPONSE, MOCK_EMAIL_RESPONSE]
        
        # Act
        result = create_or_update_person(
            mock_pco_client, "John", "Doe", 
            email="john@example.com"
        )
        
        # Assert
        assert result is not None
        assert mock_pco_client.post.call_count == 2  # Person + Email
    
    def test_create_or_update_skip_existing_email(self, mock_pco_client):
        """Test that existing email is not added again"""
        # Arrange
        existing_person = create_mock_person('12345', 'John', 'Doe')
        mock_pco_client.iterate.side_effect = [
            [existing_person],  # Person found
            MOCK_EMAIL_LIST  # Emails found
        ]
        
        # Act
        result = create_or_update_person(
            mock_pco_client, "John", "Doe",
            email="work@example.com"  # Email already exists
        )
        
        # Assert
        assert result is not None
        # Verify email post was not called
        assert not any(call[0][0].startswith('/people/v2/people/') and 'emails' in call[0][0] 
                      for call in mock_pco_client.post.call_args_list)


class TestDeletePerson:
    """Tests for delete_person function"""
    
    def test_delete_person_success(self, mock_pco_client):
        """Test successfully deleting a person"""
        # Arrange
        mock_pco_client.delete.return_value = None
        
        # Act
        result = delete_person(mock_pco_client, "12345")
        
        # Assert
        assert result is True
        mock_pco_client.delete.assert_called_once_with('/people/v2/people/12345')
    
    def test_delete_person_api_error(self, mock_pco_client):
        """Test handling of API errors during deletion"""
        # Arrange
        mock_pco_client.delete.side_effect = Exception("API Error")
        
        # Act
        result = delete_person(mock_pco_client, "12345")
        
        # Assert
        assert result is False


class TestGetPersonById:
    """Tests for get_person_by_id function"""
    
    def test_get_person_by_id_success(self, mock_pco_client):
        """Test successfully getting a person by ID"""
        # Arrange
        mock_pco_client.get.return_value = MOCK_PERSON_RESPONSE
        
        # Act
        result = get_person_by_id(mock_pco_client, "12345")
        
        # Assert
        assert result is not None
        assert result['id'] == '12345'
        assert result['attributes']['first_name'] == 'John'
        mock_pco_client.get.assert_called_once_with('/people/v2/people/12345')
    
    def test_get_person_by_id_not_found(self, mock_pco_client):
        """Test when person is not found"""
        # Arrange
        mock_pco_client.get.return_value = None
        
        # Act
        result = get_person_by_id(mock_pco_client, "99999")
        
        # Assert
        assert result is None
    
    def test_get_person_by_id_api_error(self, mock_pco_client):
        """Test handling of API errors"""
        # Arrange
        mock_pco_client.get.side_effect = Exception("API Error")
        
        # Act
        result = get_person_by_id(mock_pco_client, "12345")
        
        # Assert
        assert result is None