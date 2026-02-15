import http.client
import json

def test_login(email, password, endpoint):
    try:
        conn = http.client.HTTPConnection("localhost", 5000)
        payload = json.dumps({"email": email, "password": password})
        headers = {"Content-Type": "application/json"}
        conn.request("POST", endpoint, payload, headers)
        resp = conn.getresponse()
        data = resp.read()
        print(f"Endpoint: {endpoint}")
        print(f"Status: {resp.status}")
        print(f"Body: {data.decode()}")
    except Exception as e:
        print(f"Login test failed: {e}")

if __name__ == "__main__":
    print("Testing Patient Login...")
    test_login("angel921030chenen@gmail.com", "123456789", "/api/auth/login")
    print("\nTesting Admin Login...")
    test_login("admin@hospital.com", "admin123", "/api/admin/auth/login")
