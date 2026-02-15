"""
設定超級管理員帳號
將 staff@hospital.com 設置為 super_admin 角色
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app
from app.admin_models import HealthcareStaff, db

def setup_super_admin():
    """設置超級管理員"""
    app = create_app()
    
    with app.app_context():
        # 查找 staff@hospital.com
        admin = HealthcareStaff.query.filter_by(email='staff@hospital.com').first()
        
        if admin:
            # 更新角色
            admin.role = 'super_admin'
            db.session.commit()
            print(f"✓ 已將 {admin.email} 設置為超級管理員")
            print(f"  姓名: {admin.name}")
            print(f"  角色: {admin.role}")
        else:
            print("✗ 找不到 staff@hospital.com 帳號")
            print("  請先創建此帳號")
        
        # 顯示所有護理人員的角色
        print("\n所有護理人員列表：")
        print("=" * 70)
        print(f"{'郵箱':<30} {'姓名':<15} {'角色':<15}")
        print("-" * 70)
        
        all_staff = HealthcareStaff.query.all()
        for staff in all_staff:
            role_display = staff.role if staff.role else '(未設定)'
            print(f"{staff.email:<30} {staff.name:<15} {role_display:<15}")
        
        print("=" * 70)

if __name__ == "__main__":
    setup_super_admin()
