#!/usr/bin/env python3
"""
Quick test script to debug the add person functionality
"""

import requests
import json

def test_add_person():
    """Test adding a person"""
    url = "http://localhost:5000/api/people"
    payload = {
        "first_name": "Debug",
        "last_name": "Test",
        "gender": "Male",
        "birthdate": "1990-01-01"
    }
    
    print("Testing add person...")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("\nSending request...")
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        
        print(f"\nHTTP Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"\nResponse Body:")
        print(json.dumps(response.json(), indent=2))
        
        result = response.json()
        
        print("\n" + "="*70)
        print("Analysis:")
        print("="*70)
        print(f"Has 'id' key: {('id' in result)}")
        print(f"Has 'data' key: {('data' in result)}")
        print(f"Has 'success' key: {('success' in result)}")
        print(f"Has 'error' key: {('error' in result)}")
        
        if 'id' in result:
            print(f"Person ID: {result['id']}")
        if 'data' in result:
            print(f"Data type: {type(result['data'])}")
            if isinstance(result['data'], dict):
                print(f"Data keys: {list(result['data'].keys())}")
        
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    test_add_person()