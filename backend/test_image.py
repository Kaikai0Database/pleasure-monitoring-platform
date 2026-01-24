import requests
import os

# Test image file exists
image_path = r'c:\Users\user\Desktop\pleasure-monitoring-platform_NEW\backend\app\uploads\diary_images\2_20251208_022915_070123_xian.jpg'
print(f"Checking if image file exists: {image_path}")
print(f"File exists: {os.path.exists(image_path)}")

if os.path.exists(image_path):
    print(f"File size: {os.path.getsize(image_path)} bytes")

# Test direct URL access
image_url = 'http://localhost:5000/uploads/diary_images/2_20251208_022915_070123_xian.jpg'
print(f"\nTesting URL: {image_url}")

try:
    response = requests.get(image_url)
    print(f"Status code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print(f"Content-Length: {response.headers.get('Content-Length')}")
    
    if response.status_code == 200:
        print("✅ Image URL is accessible!")
    else:
        print(f"❌ Image URL returned error: {response.status_code}")
        print(f"Response: {response.text}")
except Exception as e:
    print(f"❌ Error accessing URL: {e}")
