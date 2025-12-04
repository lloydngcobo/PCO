"""
Mock PCO API responses for testing
"""

# Mock person responses
MOCK_PERSON_RESPONSE = {
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

MOCK_PERSON_RESPONSE_WITH_EMAILS = {
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
                'location': 'Work',
                'primary': True
            }
        },
        {
            'id': '2',
            'type': 'Email',
            'attributes': {
                'address': 'john.personal@example.com',
                'location': 'Home',
                'primary': False
            }
        }
    ]
}

MOCK_PERSON_LIST = [
    {
        'data': {
            'id': '1',
            'type': 'Person',
            'attributes': {
                'first_name': 'Alice',
                'last_name': 'Johnson',
                'gender': 'Female',
                'status': 'active',
                'membership': 'Member'
            }
        }
    },
    {
        'data': {
            'id': '2',
            'type': 'Person',
            'attributes': {
                'first_name': 'Bob',
                'last_name': 'Smith',
                'gender': 'Male',
                'status': 'active',
                'membership': 'Visitor'
            }
        }
    },
    {
        'data': {
            'id': '3',
            'type': 'Person',
            'attributes': {
                'first_name': 'Charlie',
                'last_name': 'Brown',
                'gender': 'Male',
                'status': 'inactive',
                'membership': 'Member'
            }
        }
    }
]

# Mock email responses
MOCK_EMAIL_RESPONSE = {
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

MOCK_EMAIL_LIST = [
    {
        'data': {
            'id': '1',
            'type': 'Email',
            'attributes': {
                'address': 'work@example.com',
                'location': 'Work',
                'primary': True
            }
        }
    },
    {
        'data': {
            'id': '2',
            'type': 'Email',
            'attributes': {
                'address': 'home@example.com',
                'location': 'Home',
                'primary': False
            }
        }
    }
]

# Mock campus responses
MOCK_CAMPUS_RESPONSE = {
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

MOCK_CAMPUS_LIST = [
    {
        'data': {
            'id': '1',
            'type': 'Campus',
            'attributes': {
                'name': 'Main Campus',
                'description': 'Primary location'
            }
        }
    },
    {
        'data': {
            'id': '2',
            'type': 'Campus',
            'attributes': {
                'name': 'North Campus',
                'description': 'Secondary location'
            }
        }
    }
]

# Mock error responses
MOCK_ERROR_RESPONSE = {
    'errors': [
        {
            'status': '404',
            'title': 'Not Found',
            'detail': 'The requested resource was not found'
        }
    ]
}

MOCK_VALIDATION_ERROR = {
    'errors': [
        {
            'status': '422',
            'title': 'Unprocessable Entity',
            'detail': 'Validation failed',
            'source': {
                'pointer': '/data/attributes/email'
            }
        }
    ]
}

MOCK_RATE_LIMIT_ERROR = {
    'errors': [
        {
            'status': '429',
            'title': 'Too Many Requests',
            'detail': 'Rate limit exceeded. Please try again later.'
        }
    ]
}

# Mock template responses
def mock_person_template(attributes):
    """
    Generate a mock person template payload.
    
    Args:
        attributes: Dictionary of person attributes
        
    Returns:
        dict: Mock template payload
    """
    return {
        'data': {
            'type': 'Person',
            'attributes': attributes
        }
    }


def mock_email_template(attributes):
    """
    Generate a mock email template payload.
    
    Args:
        attributes: Dictionary of email attributes
        
    Returns:
        dict: Mock template payload
    """
    return {
        'data': {
            'type': 'Email',
            'attributes': attributes
        }
    }


# Helper functions for creating mock responses
def create_mock_person(person_id='12345', first_name='John', last_name='Doe', **kwargs):
    """
    Create a custom mock person response.
    
    Args:
        person_id: Person ID
        first_name: First name
        last_name: Last name
        **kwargs: Additional attributes
        
    Returns:
        dict: Mock person response
    """
    attributes = {
        'first_name': first_name,
        'last_name': last_name,
        'gender': kwargs.get('gender', 'Male'),
        'birthdate': kwargs.get('birthdate', '1990-01-01'),
        'status': kwargs.get('status', 'active'),
        'membership': kwargs.get('membership', 'Member'),
        'created_at': kwargs.get('created_at', '2023-01-01T00:00:00Z'),
        'updated_at': kwargs.get('updated_at', '2023-06-01T00:00:00Z')
    }
    
    return {
        'data': {
            'id': person_id,
            'type': 'Person',
            'attributes': attributes
        }
    }


def create_mock_email(email_id='1', address='test@example.com', location='Work', primary=True):
    """
    Create a custom mock email response.
    
    Args:
        email_id: Email ID
        address: Email address
        location: Email location
        primary: Whether this is the primary email
        
    Returns:
        dict: Mock email response
    """
    return {
        'data': {
            'id': email_id,
            'type': 'Email',
            'attributes': {
                'address': address,
                'location': location,
                'primary': primary
            }
        }
    }