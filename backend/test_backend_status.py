"""
Quick test script to check if backend server is running and responding
"""
import requests
import sys

def test_backend():
    print("Testing backend server...")
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        print(f"✅ Backend is running!")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Backend server is NOT running!")
        print("Please start the backend server with: python run.py")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    test_backend()
