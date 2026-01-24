"""
創建三個護理師帳號
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app
from app.admin_models import HealthcareStaff, db
from werkzeug.security import generate_password_hash

def create_nurse_accounts():
    """創建三個護理師帳號"""
    app = create_app()
    
    with app.app_context():
        # 定義三個護理師帳號
        nurses = [
            {
                'name': '傅宥翔',
                'email': '123@gmail.com',
                'password': '123',
                'role': 'nurse'
            },
            {
                'name': '陳芷嫻',
                'email': '456@gmail.com',
                'password': '456',
                'role': 'nurse'
            },
            {
                'name': '陳立愷',
                'email': '789@gmail.com',
                'password': '789',
                'role': 'nurse'
            }
        ]
        
        print("開始創建護理師帳號...")
        print("=" * 60)
        
        created_count = 0
        
        for nurse_data in nurses:
            # 檢查是否已存在
            existing = HealthcareStaff.query.filter_by(email=nurse_data['email']).first()
            
            if existing:
                print(f"⚠ 帳號已存在: {nurse_data['name']} ({nurse_data['email']})")
                # 更新密碼和角色
                existing.password_hash = generate_password_hash(nurse_data['password'])
                existing.role = nurse_data['role']
                existing.name = nurse_data['name']
                print(f"  ✓ 已更新密碼和角色")
            else:
                # 創建新帳號
                nurse = HealthcareStaff(
                    name=nurse_data['name'],
                    email=nurse_data['email'],
                    password_hash=generate_password_hash(nurse_data['password']),
                    role=nurse_data['role']
                )
                db.session.add(nurse)
                print(f"✓ 創建成功: {nurse_data['name']} ({nurse_data['email']})")
                created_count += 1
        
        # 提交所有更改
        db.session.commit()
        
        print("=" * 60)
        print(f"完成！共創建/更新 {len(nurses)} 個護理師帳號\n")
        
        # 顯示所有護理師帳號
        print("所有護理師帳號列表：")
        print("=" * 60)
        print(f"{'姓名':<10} {'郵箱':<25} {'密碼':<10} {'角色':<10}")
        print("-" * 60)
        
        for nurse_data in nurses:
            print(f"{nurse_data['name']:<10} {nurse_data['email']:<25} {nurse_data['password']:<10} {nurse_data['role']:<10}")
        
        print("=" * 60)

if __name__ == "__main__":
    create_nurse_accounts()
