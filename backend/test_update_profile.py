import urllib.request
import json
import sqlite3
import os

# Login to get valid token first
LOGIN_URL = "http://localhost:5000/api/auth/login"
PROFILE_URL = "http://localhost:5000/api/auth/profile"

DB_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'database.db')

def get_test_user_cred():
    # Use the user '123' / 'angel921030chen@gmail.com' found in list_users.py
    # Or create one if not successful. 
    # Let's try registering 'test_update@example.com' first.
    return "test_update@example.com", "password123", "Test Update"

def register_user(email, password, name):
    url = "http://localhost:5000/api/auth/register"
    data = {"email": email, "password": password, "name": name}
    req = urllib.request.Request(url, method='POST')
    req.add_header('Content-Type', 'application/json')
    try:
        urllib.request.urlopen(req, json.dumps(data).encode('utf-8'))
        print("Registered user.")
    except:
        print("User might already exist.")

def test_update():
    email, password, name = get_test_user_cred()
    register_user(email, password, name)

    # Login
    login_data = {"email": email, "password": password}
    req = urllib.request.Request(LOGIN_URL, method='POST')
    req.add_header('Content-Type', 'application/json')
    
    token = None
    try:
        with urllib.request.urlopen(req, json.dumps(login_data).encode('utf-8')) as res:
            data = json.loads(res.read().decode('utf-8'))
            token = data.get('access_token')
            print("Login successful, token obtained.")
    except Exception as e:
        print(f"Login failed: {e}")
        return

    if not token:
        print("No token.")
        return

    # Update Profile Payload (Simulating full payload)
    update_data = {
        "nickname": "Tester",
        "dob": "1990-01-01",
        "gender": "生理男",
        "height": 175.5,
        "weight": 70.0,
        "education": "大學",
        "marital_status": "未婚",
        "has_children": False,
        "children_count": 0,
        "economic_status": "小康",
        "family_structure": "雙親",
        "has_job": True,
        "salary_range": "35001-50000",
        "location_city": "臺北市",
        "location_district": "信義區",
        "living_situation": "獨居",
        "cohabitant_count": 0,
        "religion": False
    }

    req = urllib.request.Request(PROFILE_URL, method='PUT')
    req.add_header('Content-Type', 'application/json')
    req.add_header('Authorization', f'Bearer {token}')
    
    print("Sending update request...")
    try:
        with urllib.request.urlopen(req, json.dumps(update_data).encode('utf-8')) as res:
            print(f"Status: {res.status}")
            print(res.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code}")
        print(e.read().decode('utf-8'))
    except Exception as e:
        print(f"Request Error: {e}")

if __name__ == '__main__':
    test_update()
