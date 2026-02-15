"""
創建超級管理員帳號
郵箱: admin@hospital.com
密碼: admin123
角色: super_admin
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app
from app.admin_models import HealthcareStaff, db
from werkzeug.security import generate_password_hash

def create_super_admin():
    """創建超級管理員帳號"""
    app = create_app()
    
    with app.app_context():
        # 檢查是否已存在
        existing = HealthcareStaff.query.filter_by(email='admin@hospital.com').first()
        
        if existing:
            print(f"[!] 帳號已存在: admin@hospital.com")
            # 更新角色和密碼
            existing.role = 'super_admin'
            existing.password_hash = generate_password_hash('admin123')
            existing.name = '超級管理員'
            db.session.commit()
            print(f"[OK] 已更新為超級管理員角色")
        else:
            # 創建新帳號
            admin = HealthcareStaff(
                email='admin@hospital.com',
                name='超級管理員',
                password_hash=generate_password_hash('admin123'),
                role='super_admin'
            )
            db.session.add(admin)
            db.session.commit()
            print(f"[OK] 創建成功: admin@hospital.com")
        
        print("\n超級管理員帳號資訊：")
        print("=" * 60)
        print(f"  郵箱: admin@hospital.com")
        print(f"  密碼: admin123")
        print(f"  角色: super_admin")
        print(f"  權限: 可查看所有病人，可分配病人給護理師")
        print("=" * 60)

if __name__ == "__main__":
    create_super_admin()
