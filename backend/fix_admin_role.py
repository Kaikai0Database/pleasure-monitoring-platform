import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.admin_models import HealthcareStaff

app = create_app()

with app.app_context():
    admin = HealthcareStaff.query.filter_by(email='admin@hospital.com').first()
    if admin:
        print(f"Admin found: {admin.email}")
        print(f"Current role: '{admin.role}'")
        print(f"Name: {admin.name}")
        
        if admin.role != 'super_admin':
            print(f"\n[FIXING] Updating role from '{admin.role}' to 'super_admin'...")
            admin.role = 'super_admin'
            db.session.commit()
            print("[OK] Role updated successfully!")
        else:
            print("\n[OK] Role is already 'super_admin'")
    else:
        print("[ERROR] Admin not found!")
