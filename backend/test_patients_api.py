"""
Test the admin patients API endpoint
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from flask_jwt_extended import create_access_token

app = create_app()

with app.app_context():
    # Create a test token for admin_1
    token = create_access_token(identity='admin_1')
    print(f"Test Token: {token}")
    print("\nTest the API with this curl command:")
    print(f'curl -X GET http://localhost:5000/api/admin/patients -H "Authorization: Bearer {token}"')
    
    # Also test the endpoint directly
    from app.routes.admin_patients import admin_patients_bp
    with app.test_client() as client:
        response = client.get('/api/admin/patients', headers={'Authorization': f'Bearer {token}'})
        print(f"\nDirect test response:")
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.content_type}")
        print(f"Data: {response.get_data(as_text=True)[:500]}")
