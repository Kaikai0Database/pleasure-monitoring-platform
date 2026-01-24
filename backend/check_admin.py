import sys
sys.path.append('c:\\Users\\user\\Desktop\\pleasure-monitoring-platform_NEW\\backend')

from app import create_app
from app.admin_models import db, HealthcareStaff
from werkzeug.security import check_password_hash

app = create_app()

with app.app_context():
    # Check if admin exists
    admin = HealthcareStaff.query.filter_by(email='admin@hospital.com').first()
    
    if admin:
        print(f"✅ Admin account found:")
        print(f"   Email: {admin.email}")
        print(f"   Name: {admin.name}")
        print(f"   Role: {admin.role}")
        print(f"   ID: {admin.id}")
        
        # Test password
        password_correct = check_password_hash(admin.password_hash, 'admin123')
        if password_correct:
            print("✅ Password is correct!")
        else:
            print("❌ Password is INCORRECT!")
            print("   Creating new admin with correct password...")
            from werkzeug.security import generate_password_hash
            admin.password_hash = generate_password_hash('admin123')
            db.session.commit()
            print("✅ Password updated!")
    else:
        print("❌ Admin account NOT found!")
        print("   Creating admin account...")
        from werkzeug.security import generate_password_hash
        new_admin = HealthcareStaff(
            email='admin@hospital.com',
            name='Administrator',
            password_hash=generate_password_hash('admin123'),
            role='系統管理員'
        )
        db.session.add(new_admin)
        db.session.commit()
        print("✅ Admin account created!")
