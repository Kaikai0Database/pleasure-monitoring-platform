import http.client
import json

def check_health():
    try:
        conn = http.client.HTTPConnection("localhost", 5000)
        conn.request("GET", "/api/health")
        resp = conn.getresponse()
        data = resp.read()
        print(f"Status: {resp.status}")
        print(f"Body: {data.decode()}")
    except Exception as e:
        print(f"Health check failed: {e}")

if __name__ == "__main__":
    check_health()
