#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to add email address to the test user
Person ID: 182133595
Email: ap@example.com
"""

import os
import sys
from dotenv import load_dotenv
from src.pco_helpers import get_pco_client, add_email_to_person

# Load environment variables
load_dotenv()

# Test user details
PERSON_ID = "182133595"
EMAIL_ADDRESS = "ap@example.com"

def add_email_to_test_user():
    """Add email address to the test user"""
    try:
        # Get PCO client
        print("Connecting to Planning Center Online...")
        pco = get_pco_client()
        print("[SUCCESS] Connected successfully!\n")
        
        # Add email to the test user
        print(f"Adding email to test user (ID: {PERSON_ID})...")
        print(f"Email: {EMAIL_ADDRESS}")
        print()
        
        email = add_email_to_person(
            pco=pco,
            person_id=PERSON_ID,
            email_address=EMAIL_ADDRESS,
            location="Home"  # Email location type
        )
        
        if email:
            print("[SUCCESS] Email added successfully!")
            print(f"\nEmail Details:")
            print(f"  Email ID: {email.get('id')}")
            print(f"  Address: {email.get('attributes', {}).get('address')}")
            print(f"  Location: {email.get('attributes', {}).get('location')}")
            print(f"  Primary: {email.get('attributes', {}).get('primary')}")
            print(f"  Created At: {email.get('attributes', {}).get('created_at')}")
            return email
        else:
            print("[ERROR] Failed to add email")
            print("The email might already exist or there was an API error.")
            return None
            
    except ValueError as e:
        print(f"[ERROR] {e}")
        print("\nPlease ensure PCO_APP_ID and PCO_SECRET are set in your .env file")
        return None
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("Add Email to PCO Test User")
    print("=" * 60)
    print()
    
    email = add_email_to_test_user()
    
    print()
    print("=" * 60)
    if email:
        print("[SUCCESS] Email addition completed successfully!")
    else:
        print("[ERROR] Email addition failed. Please check the errors above.")
    print("=" * 60)