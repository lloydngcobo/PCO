"""
Example usage of PCO API Wrapper utility functions
Demonstrates common operations with Planning Center Online
"""

import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.pco_helpers import (
    get_pco_client,
    find_person_by_name,
    add_person,
    update_person_attribute,
    update_person_attributes,
    add_email_to_person,
    get_person_emails,
    create_or_update_person,
    delete_person,
    get_person_by_id
)


def example_1_create_person():
    """Example 1: Create a new person"""
    print("\n=== Example 1: Create a New Person ===")
    
    pco = get_pco_client()
    
    person = add_person(
        pco,
        first_name="John",
        last_name="Doe",
        gender="Male",
        birthdate="1990-01-01",
        check_duplicate=True
    )
    
    if person:
        print(f"✓ Created person with ID: {person['id']}")
        return person['id']
    else:
        print("✗ Person already exists or creation failed")
        return None


def example_2_find_person():
    """Example 2: Find a person by name"""
    print("\n=== Example 2: Find Person by Name ===")
    
    pco = get_pco_client()
    
    person = find_person_by_name(pco, "John", "Doe")
    
    if person:
        print(f"✓ Found person: {person['attributes']['first_name']} {person['attributes']['last_name']}")
        print(f"  ID: {person['id']}")
        print(f"  Status: {person['attributes']['status']}")
        return person['id']
    else:
        print("✗ Person not found")
        return None


def example_3_update_person(person_id):
    """Example 3: Update person attributes"""
    print("\n=== Example 3: Update Person Attributes ===")
    
    if not person_id:
        print("✗ No person ID provided")
        return
    
    pco = get_pco_client()
    
    # Update single attribute
    updated = update_person_attribute(pco, person_id, "gender", "Male")
    
    if updated:
        print(f"✓ Updated gender for person {person_id}")
    
    # Update multiple attributes
    updated = update_person_attributes(
        pco,
        person_id,
        {
            "birthdate": "1990-01-01",
            "gender": "Male"
        }
    )
    
    if updated:
        print(f"✓ Updated multiple attributes for person {person_id}")


def example_4_manage_emails(person_id):
    """Example 4: Manage email addresses"""
    print("\n=== Example 4: Manage Email Addresses ===")
    
    if not person_id:
        print("✗ No person ID provided")
        return
    
    pco = get_pco_client()
    
    # Add email
    email = add_email_to_person(
        pco,
        person_id,
        "john.doe@example.com",
        "Work"
    )
    
    if email:
        print(f"✓ Added email: {email['attributes']['address']}")
    
    # Get all emails
    emails = get_person_emails(pco, person_id)
    print(f"\n✓ Person has {len(emails)} email(s):")
    for email in emails:
        print(f"  - {email['address']} ({email['location']})")


def example_5_create_or_update():
    """Example 5: Create or update person (idempotent operation)"""
    print("\n=== Example 5: Create or Update Person ===")
    
    pco = get_pco_client()
    
    person = create_or_update_person(
        pco,
        first_name="Jane",
        last_name="Smith",
        gender="Female",
        birthdate="1985-05-15",
        email="jane.smith@example.com",
        email_location="Work"
    )
    
    if person:
        print(f"✓ Person ready: {person['attributes']['first_name']} {person['attributes']['last_name']}")
        print(f"  ID: {person['id']}")
        return person['id']
    else:
        print("✗ Operation failed")
        return None


def example_6_get_person_details(person_id):
    """Example 6: Get complete person details"""
    print("\n=== Example 6: Get Person Details ===")
    
    if not person_id:
        print("✗ No person ID provided")
        return
    
    pco = get_pco_client()
    
    person = get_person_by_id(pco, person_id)
    
    if person:
        attrs = person['attributes']
        print(f"✓ Person Details:")
        print(f"  ID: {person['id']}")
        print(f"  Name: {attrs.get('first_name')} {attrs.get('last_name')}")
        print(f"  Gender: {attrs.get('gender', 'N/A')}")
        print(f"  Birthdate: {attrs.get('birthdate', 'N/A')}")
        print(f"  Status: {attrs.get('status')}")
        print(f"  Membership: {attrs.get('membership', 'N/A')}")
        print(f"  Created: {attrs.get('created_at')}")
        print(f"  Updated: {attrs.get('updated_at')}")


def example_7_delete_person(person_id):
    """Example 7: Delete a person (use with caution!)"""
    print("\n=== Example 7: Delete Person ===")
    
    if not person_id:
        print("✗ No person ID provided")
        return
    
    # Uncomment the following lines to actually delete
    # WARNING: This will permanently delete the person!
    
    # pco = get_pco_client()
    # success = delete_person(pco, person_id)
    # 
    # if success:
    #     print(f"✓ Deleted person {person_id}")
    # else:
    #     print(f"✗ Failed to delete person {person_id}")
    
    print(f"⚠ Delete operation commented out for safety")
    print(f"  Uncomment code in example_7_delete_person() to enable deletion")


def main():
    """Run all examples"""
    print("=" * 60)
    print("PCO API Wrapper - Example Usage")
    print("=" * 60)
    
    try:
        # Example 1: Create a person
        person_id = example_1_create_person()
        
        # Example 2: Find the person
        if not person_id:
            person_id = example_2_find_person()
        
        # Example 3: Update person attributes
        if person_id:
            example_3_update_person(person_id)
        
        # Example 4: Manage emails
        if person_id:
            example_4_manage_emails(person_id)
        
        # Example 5: Create or update (idempotent)
        jane_id = example_5_create_or_update()
        
        # Example 6: Get person details
        if jane_id:
            example_6_get_person_details(jane_id)
        
        # Example 7: Delete person (commented out for safety)
        # example_7_delete_person(person_id)
        
        print("\n" + "=" * 60)
        print("✓ All examples completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()