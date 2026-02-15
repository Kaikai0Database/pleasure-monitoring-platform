"""
創建測試專家帳號 experttest2@gmail.com
角色: super_admin
密碼: test123
全域最高權限，可查看所有患者
"""

from app import create_app
from app.admin_models import db, HealthcareStaff
from werkzeug.security import generate_password_hash

def create_experttest2():
    app = create_app()
    with app.app_context():
        # 檢查是否已存在
        existing = HealthcareStaff.query.filter_by(email='experttest2@gmail.com').first()
        
        if existing:
            print(f"\n⚠️  帳號 experttest2@gmail.com 已存在")
            print(f"  ID: {existing.id}")
            print(f"  姓名: {existing.name}")
            print(f"  角色: {existing.role}")
            print(f"\n將更新為 super_admin 角色...")
            
            existing.role = 'super_admin'
            existing.password_hash = generate_password_hash('test123')
            db.session.commit()
            print("✅ 角色與密碼已更新")
        else:
            # 創建新帳號
            new_admin = HealthcareStaff(
                name='Expert Test 2',
                email='experttest2@gmail.com',
                password_hash=generate_password_hash('test123'),
                role='super_admin'
            )
            
            db.session.add(new_admin)
            db.session.commit()
            
            print("\n✅ 超級管理員帳號創建成功！")
            print(f"  ID: {new_admin.id}")
            print(f"  姓名: {new_admin.name}")
            print(f"  Email: {new_admin.email}")
            print(f"  角色: super_admin")
            print(f"  密碼: test123")

if __name__ == '__main__':
    create_experttest2()
