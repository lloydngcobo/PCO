#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to check existing emails and add email address to the test user
Person ID: 182133595
Email: ap@example.com
"""

import os
import sys
from dotenv import load_dotenv
from src.pco_helpers import get_pco_client, get_person_emails

# Load environment variables
load_dotenv()

# Test user details
PERSON_ID = "182133595"
EMAIL_ADDRESS = "ap@example.com"

def check_and_add_email():
    """Check existing emails and try to add new email"""
    try:
        # Get PCO client
        print("Connecting to Planning Center Online...")
        pco = get_pco_client()
        print("[SUCCESS] Connected successfully!\n")
        
        # First, check existing emails
        print(f"Checking existing emails for person ID: {PERSON_ID}...")
        existing_emails = get_person_emails(pco, PERSON_ID)
        
        if existing_emails:
            print(f"\n[INFO] Found {len(existing_emails)} existing email(s):")
            for email in existing_emails:
                print(f"  - {email.get('attributes', {}).get('address')} ({email.get('attributes', {}).get('location')})")
        else:
            print("[INFO] No existing emails found")
        
        print(f"\n[INFO] Attempting to add email via PCO API directly...")
        print(f"Email: {EMAIL_ADDRESS}")
        print(f"Location: Home")
        
        # Try to add email using direct API call
        try:
            email_payload = {
                "data": {
                    "type": "Email",
                    "attributes": {
                        "address": EMAIL_ADDRESS,
                        "location": "Home"
                    }
                }
            }
            
            response = pco.post(f'/people/v2/people/{PERSON_ID}/emails', email_payload)
            
            if response and 'data' in response:
                email_data = response['data']
                print("\n[SUCCESS] Email added successfully!")
                print(f"\nEmail Details:")
                print(f"  Email ID: {email_data.get('id')}")
                print(f"  Address: {email_data.get('attributes', {}).get('address')}")
                print(f"  Location: {email_data.get('attributes', {}).get('location')}")
                print(f"  Primary: {email_data.get('attributes', {}).get('primary')}")
                return email_data
            else:
                print("[ERROR] Unexpected response format")
                return None
                
        except Exception as api_error:
            print(f"\n[ERROR] PCO API Error: {api_error}")
            print("\n[INFO] This error typically occurs when:")
            print("  1. The email address already exists for this person")
            print("  2. The email format is invalid")
            print("  3. PCO account permissions don't allow email additions")
            print("  4. There are validation rules in your PCO account")
            
            # Check if email already exists
            if existing_emails:
                for email in existing_emails:
                    if email.get('attributes', {}).get('address') == EMAIL_ADDRESS:
                        print(f"\n[NOTE] The email '{EMAIL_ADDRESS}' already exists for this person!")
                        return email
            
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
    print("Check and Add Email to PCO Test User")
    print("=" * 60)
    print()
    
    result = check_and_add_email()
    
    print()
    print("=" * 60)
    if result:
        print("[SUCCESS] Operation completed!")
    else:
        print("[INFO] Could not add email. See details above.")
    print("=" * 60)