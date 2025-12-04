"""
PCO Helper Functions with Caching
Enhanced version of pco_helpers.py with caching support
"""

import pypco
from dotenv import load_dotenv
import os
from typing import Optional, Dict, Any, List
from cache import cached, invalidate_cache, get_cache_manager

# Load environment variables
load_dotenv()


def get_pco_client() -> pypco.PCO:
    """
    Initialize and return a PCO client with credentials from environment variables.
    
    Returns:
        pypco.PCO: Initialized PCO client
        
    Raises:
        ValueError: If PCO_APP_ID or PCO_SECRET are not set
    """
    PCO_APP_ID = os.getenv("PCO_APP_ID")
    PCO_SECRET = os.getenv("PCO_SECRET")
    
    if not PCO_APP_ID or not PCO_SECRET:
        raise ValueError("PCO_APP_ID and PCO_SECRET must be set in the .env file")
    
    return pypco.PCO(PCO_APP_ID, PCO_SECRET)


@cached(ttl=300)  # Cache for 5 minutes
def find_person_by_name(pco: pypco.PCO, first_name: str, last_name: str) -> Optional[Dict[str, Any]]:
    """
    Search for a person by first and last name (with caching).
    
    Args:
        pco: Initialized PCO client
        first_name: Person's first name
        last_name: Person's last name
        
    Returns:
        Dict containing person data if found, None otherwise
        
    Example:
        >>> pco = get_pco_client()
        >>> person = find_person_by_name(pco, "John", "Doe")
        >>> if person:
        ...     print(f"Found person with ID: {person['id']}")
    """
    print(f"Searching for {first_name} {last_name}...")
    
    try:
        for person in pco.iterate('/people/v2/people'):
            attributes = person['data']['attributes']
            if attributes.get('first_name') == first_name and attributes.get('last_name') == last_name:
                print(f"Found {first_name} {last_name} with ID: {person['data']['id']}")
                return {
                    'id': person['data']['id'],
                    'data': person['data'],
                    'attributes': attributes
                }
    except Exception as e:
        print(f"ERROR: Error searching for person: {e}")
        return None
    
    print(f"{first_name} {last_name} not found")
    return None


def add_person(pco: pypco.PCO, first_name: str, last_name: str, 
               gender: Optional[str] = None, 
               birthdate: Optional[str] = None,
               check_duplicate: bool = True) -> Optional[Dict[str, Any]]:
    """
    Add a new person to PCO (invalidates cache).
    
    Args:
        pco: Initialized PCO client
        first_name: Person's first name
        last_name: Person's last name
        gender: Optional gender (Male, Female, or None)
        birthdate: Optional birthdate in YYYY-MM-DD format
        check_duplicate: Whether to check for existing person before creating
        
    Returns:
        Dict containing new person data if successful, None if person exists or error occurs
    """
    # Check for duplicates if requested
    if check_duplicate:
        existing_person = find_person_by_name(pco, first_name, last_name)
        if existing_person:
            print(f"NOTICE: {first_name} {last_name} already exists with ID: {existing_person['id']}")
            return None
    
    # Create payload
    attributes = {
        'first_name': first_name,
        'last_name': last_name
    }
    
    if gender:
        attributes['gender'] = gender
    if birthdate:
        attributes['birthdate'] = birthdate
    
    payload = pco.template('Person', attributes)
    
    # Add the person
    try:
        new_person = pco.post('/people/v2/people', payload)
        person_data = {
            'id': new_person['data']['id'],
            'data': new_person['data'],
            'attributes': new_person['data']['attributes']
        }
        
        print("SUCCESS: Successfully added new person!")
        print(f"Person ID: {person_data['id']}")
        print(f"Name: {person_data['attributes']['first_name']} {person_data['attributes']['last_name']}")
        if gender:
            print(f"Gender: {person_data['attributes']['gender']}")
        print(f"Status: {person_data['attributes']['status']}")
        print(f"Created At: {person_data['attributes']['created_at']}")
        
        # Invalidate find_person_by_name cache for this person
        invalidate_cache('find_person_by_name', pco, first_name, last_name)
        
        return person_data
        
    except Exception as e:
        print(f"ERROR: Error adding person: {e}")
        return None


def update_person_attribute(pco: pypco.PCO, person_id: str, 
                           attribute_name: str, attribute_value: Any) -> Optional[Dict[str, Any]]:
    """
    Update a single attribute for a person (invalidates cache).
    
    Args:
        pco: Initialized PCO client
        person_id: The person's ID
        attribute_name: Name of the attribute to update
        attribute_value: New value for the attribute
        
    Returns:
        Dict containing updated person data if successful, None otherwise
    """
    try:
        payload = pco.template('Person', {attribute_name: attribute_value})
        updated_person = pco.patch(f'/people/v2/people/{person_id}', payload)
        
        print(f"SUCCESS: Updated {attribute_name} to {attribute_value}")
        
        # Invalidate get_person_by_id cache
        invalidate_cache('get_person_by_id', pco, person_id)
        
        return {
            'id': updated_person['data']['id'],
            'data': updated_person['data'],
            'attributes': updated_person['data']['attributes']
        }
        
    except Exception as e:
        print(f"ERROR: Error updating {attribute_name}: {e}")
        return None


def update_person_attributes(pco: pypco.PCO, person_id: str, 
                            attributes: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Update multiple attributes for a person (invalidates cache).
    
    Args:
        pco: Initialized PCO client
        person_id: The person's ID
        attributes: Dictionary of attributes to update
        
    Returns:
        Dict containing updated person data if successful, None otherwise
    """
    try:
        payload = pco.template('Person', attributes)
        updated_person = pco.patch(f'/people/v2/people/{person_id}', payload)
        
        print(f"SUCCESS: Updated {len(attributes)} attribute(s)")
        
        # Invalidate get_person_by_id cache
        invalidate_cache('get_person_by_id', pco, person_id)
        
        return {
            'id': updated_person['data']['id'],
            'data': updated_person['data'],
            'attributes': updated_person['data']['attributes']
        }
        
    except Exception as e:
        print(f"ERROR: Error updating attributes: {e}")
        return None


@cached(ttl=600)  # Cache for 10 minutes
def get_person_by_id(pco: pypco.PCO, person_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a person by their ID (with caching).
    
    Args:
        pco: Initialized PCO client
        person_id: The person's ID
        
    Returns:
        Dict containing person data if found, None otherwise
    """
    try:
        person = pco.get(f'/people/v2/people/{person_id}')
        
        if person:
            return {
                'id': person['data']['id'],
                'data': person['data'],
                'attributes': person['data']['attributes']
            }
        return None
        
    except Exception as e:
        print(f"ERROR: Error fetching person: {e}")
        return None


@cached(ttl=600)  # Cache for 10 minutes
def get_person_emails(pco: pypco.PCO, person_id: str) -> List[Dict[str, Any]]:
    """
    Get all email addresses for a person (with caching).
    
    Args:
        pco: Initialized PCO client
        person_id: The person's ID
        
    Returns:
        List of email dictionaries
    """
    try:
        emails = []
        for email in pco.iterate(f'/people/v2/people/{person_id}/emails'):
            emails.append({
                'id': email['data']['id'],
                'address': email['data']['attributes']['address'],
                'location': email['data']['attributes']['location'],
                'primary': email['data']['attributes'].get('primary', False)
            })
        return emails
        
    except Exception as e:
        print(f"ERROR: Error fetching emails: {e}")
        return []


def add_email_to_person(pco: pypco.PCO, person_id: str, 
                       email_address: str, location: str = "Work") -> Optional[Dict[str, Any]]:
    """
    Add an email address to a person (invalidates cache).
    
    Args:
        pco: Initialized PCO client
        person_id: The person's ID
        email_address: Email address to add
        location: Email location (Work, Home, etc.)
        
    Returns:
        Dict containing email data if successful, None otherwise
    """
    try:
        email_payload = {
            "data": {
                "type": "Email",
                "attributes": {
                    "address": email_address,
                    "location": location
                }
            }
        }
        
        email_response = pco.post(f'/people/v2/people/{person_id}/emails', email_payload)
        
        print(f"SUCCESS: Email added - {email_address} ({location})")
        
        # Invalidate get_person_emails cache
        invalidate_cache('get_person_emails', pco, person_id)
        
        return {
            'id': email_response['data']['id'],
            'data': email_response['data'],
            'attributes': email_response['data']['attributes']
        }
        
    except Exception as e:
        print(f"ERROR: Error adding email: {e}")
        return None


def update_email(pco: pypco.PCO, person_id: str, email_id: str,
                email_address: Optional[str] = None,
                location: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Update an email address for a person (invalidates cache).
    
    Args:
        pco: Initialized PCO client
        person_id: The person's ID
        email_id: The email's ID
        email_address: New email address (optional)
        location: New location (optional)
        
    Returns:
        Dict containing updated email data if successful, None otherwise
    """
    try:
        attributes = {}
        if email_address:
            attributes['address'] = email_address
        if location:
            attributes['location'] = location
        
        email_payload = {
            "data": {
                "type": "Email",
                "attributes": attributes
            }
        }
        
        email_response = pco.patch(
            f'/people/v2/people/{person_id}/emails/{email_id}',
            email_payload
        )
        
        print(f"SUCCESS: Email updated")
        
        # Invalidate get_person_emails cache
        invalidate_cache('get_person_emails', pco, person_id)
        
        return {
            'id': email_response['data']['id'],
            'data': email_response['data'],
            'attributes': email_response['data']['attributes']
        }
        
    except Exception as e:
        print(f"ERROR: Error updating email: {e}")
        return None


def delete_email(pco: pypco.PCO, person_id: str, email_id: str) -> bool:
    """
    Delete an email address from a person (invalidates cache).
    
    Args:
        pco: Initialized PCO client
        person_id: The person's ID
        email_id: The email's ID
        
    Returns:
        True if successful, False otherwise
    """
    try:
        pco.delete(f'/people/v2/people/{person_id}/emails/{email_id}')
        print(f"SUCCESS: Email {email_id} deleted")
        
        # Invalidate get_person_emails cache
        invalidate_cache('get_person_emails', pco, person_id)
        
        return True
        
    except Exception as e:
        print(f"ERROR: Error deleting email: {e}")
        return False


def delete_person(pco: pypco.PCO, person_id: str) -> bool:
    """
    Delete a person from PCO (invalidates cache).
    
    Args:
        pco: Initialized PCO client
        person_id: The person's ID to delete
        
    Returns:
        True if successful, False otherwise
    """
    try:
        pco.delete(f'/people/v2/people/{person_id}')
        print(f"SUCCESS: Person {person_id} deleted")
        
        # Invalidate get_person_by_id cache
        invalidate_cache('get_person_by_id', pco, person_id)
        
        return True
        
    except Exception as e:
        print(f"ERROR: Error deleting person: {e}")
        return False


def create_or_update_person(pco: pypco.PCO, first_name: str, last_name: str,
                           gender: Optional[str] = None, 
                           birthdate: Optional[str] = None,
                           email: Optional[str] = None,
                           email_location: str = "Work") -> Optional[Dict[str, Any]]:
    """
    Create a new person or update if they already exist (with cache management).
    
    Args:
        pco: Initialized PCO client
        first_name: Person's first name
        last_name: Person's last name
        gender: Optional gender
        birthdate: Optional birthdate in YYYY-MM-DD format
        email: Optional email address to add
        email_location: Email location if email is provided
        
    Returns:
        Dict containing person data
    """
    # Check if person exists (uses cache)
    person = find_person_by_name(pco, first_name, last_name)
    
    if not person:
        # Create new person (invalidates cache automatically)
        person = add_person(pco, first_name, last_name, gender, birthdate, check_duplicate=False)
        if not person:
            return None
    else:
        print(f"Person already exists. Updating if needed...")
        
        # Update attributes if provided and different
        updates = {}
        if gender and person['attributes'].get('gender') != gender:
            updates['gender'] = gender
        if birthdate and person['attributes'].get('birthdate') != birthdate:
            updates['birthdate'] = birthdate
        
        if updates:
            update_person_attributes(pco, person['id'], updates)
    
    # Add email if provided
    if email:
        # Check if email already exists (uses cache)
        existing_emails = get_person_emails(pco, person['id'])
        email_exists = any(e['address'] == email for e in existing_emails)
        
        if not email_exists:
            add_email_to_person(pco, person['id'], email, email_location)
        else:
            print(f"Email {email} already exists for this person")
    
    return person