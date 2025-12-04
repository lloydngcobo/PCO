#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to create a test user in Planning Center Online
First Name: api
Last Name: test
"""

import os
import sys
from dotenv import load_dotenv
from src.pco_helpers import get_pco_client, add_person

# Load environment variables
load_dotenv()

def create_test_user():
    """Create a test user with first name 'api' and last name 'test'"""
    try:
        # Get PCO client
        print("Connecting to Planning Center Online...")
        pco = get_pco_client()
        print("[SUCCESS] Connected successfully!\n")
        
        # Create the test user
        print("Creating test user...")
        print("First Name: api")
        print("Last Name: test")
        print()
        
        person = add_person(
            pco=pco,
            first_name="api",
            last_name="test",
            check_duplicate=True  # Check if user already exists
        )
        
        if person:
            print("[SUCCESS] Test user created successfully!")
            print(f"\nPerson Details:")
            print(f"  ID: {person.get('id')}")
            print(f"  Name: {person.get('attributes', {}).get('name')}")
            print(f"  First Name: {person.get('attributes', {}).get('first_name')}")
            print(f"  Last Name: {person.get('attributes', {}).get('last_name')}")
            print(f"  Status: {person.get('attributes', {}).get('status')}")
            print(f"  Created At: {person.get('attributes', {}).get('created_at')}")
            print(f"\n[NOTE] Save this Person ID for future reference!")
            return person
        else:
            print("[ERROR] Failed to create test user")
            print("This might mean the user already exists.")
            return None
            
    except ValueError as e:
        print(f"[ERROR] {e}")
        print("\nPlease ensure PCO_APP_ID and PCO_SECRET are set in your .env file")
        return None
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred: {e}")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("PCO Test User Creation Script")
    print("=" * 60)
    print()
    
    person = create_test_user()
    
    print()
    print("=" * 60)
    if person:
        print("[SUCCESS] Test user creation completed successfully!")
    else:
        print("[ERROR] Test user creation failed. Please check the errors above.")
    print("=" * 60)