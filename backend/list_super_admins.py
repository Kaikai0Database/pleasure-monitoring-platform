
from app import create_app
from app.admin_models import HealthcareStaff

app = create_app()

with app.app_context():
    admins = HealthcareStaff.query.filter_by(role='super_admin').all()
    print("="*50)
    print("超級管理員列表 (Super Admins)")
    print("="*50)
    
    if not admins:
        print("未找到任何超級管理員帳號")
    
    for admin in admins:
        print(f"姓名: {admin.name}")
        print(f"Email: {admin.email}")
        print(f"ID: {admin.id}")
        print("-" * 30)
    
    print("="*50)
    print("注意：密碼已加密儲存，無法直接查看。")
    print("若忘記密碼，請使用 create_pi_admin.py 重置為預設密碼。")
