"""
Check if super admin exists and create if not
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.admin_models import HealthcareStaff
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Check if super admin exists
    admin = HealthcareStaff.query.filter_by(email='admin@hospital.com').first()
    
    if admin:
        print("[OK] Super admin already exists!")
        print(f"  Email: {admin.email}")
        print(f"  Name: {admin.name}")
        print(f"  Role: {admin.role}")
        print(f"  ID: {admin.id}")
        print(f"  Created: {admin.created_at}")
    else:
        print("[INFO] Super admin not found. Creating...")
        
        # Create super admin
        admin = HealthcareStaff(
            email='admin@hospital.com',
            name='Super Admin',
            password_hash=generate_password_hash('admin123'),
            role='系統管理員'
        )
        
        db.session.add(admin)
        db.session.commit()
        
        print("[SUCCESS] Super admin created!")
        print(f"  Email: admin@hospital.com")
        print(f"  Password: admin123")
        print(f"  Name: Super Admin")
        print(f"  Role: 系統管理員")
        print(f"  ID: {admin.id}")
    
    print("\n" + "="*60)
    print("You can now login to admin dashboard:")
    print("  URL: http://localhost:5174")
    print("  Email: admin@hospital.com")
    print("  Password: admin123")
    print("="*60)
