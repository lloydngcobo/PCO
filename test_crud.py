"""
Test CRUD Operations for PCO API Wrapper
Demonstrates Create, Read, Update, Delete operations
"""

import requests
import json
import time

# API Base URL
BASE_URL = "http://localhost:5000"

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_response(response, operation):
    """Print formatted response"""
    print(f"\n{operation}:")
    print(f"Status Code: {response.status_code}")
    if response.status_code < 400:
        print("✅ Success")
        try:
            data = response.json()
            print(json.dumps(data, indent=2))
        except:
            print(response.text)
    else:
        print("❌ Error")
        print(response.text)
    print("-" * 60)

def test_health_check():
    """Test 1: Health Check"""
    print_section("TEST 1: Health Check")
    
    response = requests.get(f"{BASE_URL}/health")
    print_response(response, "GET /health")
    
    return response.status_code == 200

def test_get_campuses():
    """Test 2: Get All Campuses"""
    print_section("TEST 2: Get All Campuses")
    
    response = requests.get(f"{BASE_URL}/api/campuses")
    print_response(response, "GET /api/campuses")
    
    return response.status_code == 200

def test_get_all_people():
    """Test 3: Get All People (first 5)"""
    print_section("TEST 3: Get All People")
    
    response = requests.get(f"{BASE_URL}/api/people")
    print_response(response, "GET /api/people")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nTotal people found: {data.get('count', 0)}")
        if data.get('data'):
            print("\nFirst 5 people:")
            for person in data['data'][:5]:
                print(f"  - {person['first_name']} {person['last_name']} (ID: {person['id']})")
    
    return response.status_code == 200

def test_get_people_by_role():
    """Test 4: Get People by Role"""
    print_section("TEST 4: Get People by Role (Member)")
    
    response = requests.get(f"{BASE_URL}/api/people?role=member")
    print_response(response, "GET /api/people?role=member")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nMembers found: {data.get('count', 0)}")
    
    return response.status_code == 200

def test_create_person():
    """Test 5: Create a New Person"""
    print_section("TEST 5: Create a New Person")
    
    new_person = {
        "first_name": "API",
        "last_name": "Test",
        "gender": "Male"
    }
    
    print(f"\nCreating person: {json.dumps(new_person, indent=2)}")
    
    response = requests.post(
        f"{BASE_URL}/api/people",
        headers={"Content-Type": "application/json"},
        json=new_person
    )
    print_response(response, "POST /api/people")
    
    if response.status_code == 201:
        data = response.json()
        person_id = data.get('id')
        print(f"\n✅ Created person with ID: {person_id}")
        return person_id
    
    return None

def test_get_person_by_id(person_id):
    """Test 6: Get Specific Person by ID"""
    print_section(f"TEST 6: Get Person by ID ({person_id})")
    
    if not person_id:
        print("⚠️  No person ID provided, skipping test")
        return False
    
    response = requests.get(f"{BASE_URL}/api/people/{person_id}")
    print_response(response, f"GET /api/people/{person_id}")
    
    return response.status_code == 200

def test_update_person(person_id):
    """Test 7: Update Person"""
    print_section(f"TEST 7: Update Person ({person_id})")
    
    if not person_id:
        print("⚠️  No person ID provided, skipping test")
        return False
    
    updates = {
        "gender": "Female",
        "birthdate": "1990-01-01"
    }
    
    print(f"\nUpdating person with: {json.dumps(updates, indent=2)}")
    
    response = requests.patch(
        f"{BASE_URL}/api/people/{person_id}",
        headers={"Content-Type": "application/json"},
        json=updates
    )
    print_response(response, f"PATCH /api/people/{person_id}")
    
    return response.status_code == 200

def test_delete_person(person_id):
    """Test 8: Delete Person"""
    print_section(f"TEST 8: Delete Person ({person_id})")
    
    if not person_id:
        print("⚠️  No person ID provided, skipping test")
        return False
    
    # Ask for confirmation
    print(f"\n⚠️  WARNING: This will permanently delete person {person_id}")
    print("Proceeding with deletion in 2 seconds...")
    time.sleep(2)
    
    response = requests.delete(f"{BASE_URL}/api/people/{person_id}")
    print_response(response, f"DELETE /api/people/{person_id}")
    
    return response.status_code == 200

def test_get_people_text_format():
    """Test 9: Get People in Text Format"""
    print_section("TEST 9: Get People in Text Format")
    
    response = requests.get(f"{BASE_URL}/api/people?format=text")
    print_response(response, "GET /api/people?format=text")
    
    return response.status_code == 200

def main():
    """Run all CRUD tests"""
    print("\n" + "🚀" * 30)
    print("  PCO API WRAPPER - CRUD OPERATIONS TEST")
    print("🚀" * 30)
    
    results = []
    person_id = None
    
    try:
        # Test 1: Health Check
        results.append(("Health Check", test_health_check()))
        
        # Test 2: Get Campuses
        results.append(("Get Campuses", test_get_campuses()))
        
        # Test 3: Get All People
        results.append(("Get All People", test_get_all_people()))
        
        # Test 4: Get People by Role
        results.append(("Get People by Role", test_get_people_by_role()))
        
        # Test 5: Create Person (CREATE)
        person_id = test_create_person()
        results.append(("Create Person", person_id is not None))
        
        if person_id:
            # Test 6: Get Person by ID (READ)
            results.append(("Get Person by ID", test_get_person_by_id(person_id)))
            
            # Test 7: Update Person (UPDATE)
            results.append(("Update Person", test_update_person(person_id)))
            
            # Test 8: Delete Person (DELETE)
            results.append(("Delete Person", test_delete_person(person_id)))
        
        # Test 9: Get People in Text Format
        results.append(("Get People (Text)", test_get_people_text_format()))
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to the API server")
        print("Make sure the Flask server is running on http://localhost:5000")
        return
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Print Summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nTests Passed: {passed}/{total}")
    print("\nDetailed Results:")
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    if passed == total:
        print("\n🎉 All tests passed successfully!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
    
    print("\n" + "="*60)
    print("  CRUD Operations Test Complete")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()