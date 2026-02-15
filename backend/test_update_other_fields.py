import urllib.request
import json
import os

LOGIN_URL = "http://localhost:5000/api/auth/login"
PROFILE_URL = "http://localhost:5000/api/auth/profile"

# Use previous valid credentials or register new ones if needed
EMAIL = "test_update@example.com"
PASSWORD = "password123"

def test_other_fields():
    # 1. Login
    login_data = {"email": EMAIL, "password": PASSWORD}
    req = urllib.request.Request(LOGIN_URL, method='POST')
    req.add_header('Content-Type', 'application/json')
    
    token = None
    try:
        with urllib.request.urlopen(req, json.dumps(login_data).encode('utf-8')) as res:
            data = json.loads(res.read().decode('utf-8'))
            token = data.get('access_token')
            print("Login successful.")
    except Exception as e:
        print(f"Login failed: {e}")
        return

    # 2. Update with "Other" fields
    update_data = {
        "marital_status": "其他",
        "marriage_other": "Testing Marriage Other",
        "family_structure": "其他",
        "family_other": "Testing Family Other",
        "religion": False, # Just to keep other required fields or existing ones
    }

    req = urllib.request.Request(PROFILE_URL, method='PUT')
    req.add_header('Content-Type', 'application/json')
    req.add_header('Authorization', f'Bearer {token}')
    
    print("Updating 'Other' fields...")
    try:
        with urllib.request.urlopen(req, json.dumps(update_data).encode('utf-8')) as res:
            print(f"Status: {res.status}")
            print(res.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code}")
        print(e.read().decode('utf-8'))

if __name__ == '__main__':
    test_other_fields()
