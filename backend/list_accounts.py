"""
列出所有用戶帳號並重置為統一測試密碼
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app
from app.models import db, User
from werkzeug.security import generate_password_hash

def list_and_reset_passwords():
    """列出所有用戶並重置密碼為 test123"""
    app = create_app()
    
    with app.app_context():
        # 獲取所有用戶
        users = User.query.all()
        
        if not users:
            print("沒有找到任何用戶！")
            return
        
        print(f"找到 {len(users)} 個用戶帳號")
        print("=" * 70)
        print(f"{'編號':<4} {'郵箱':<40} {'名稱':<20}")
        print("=" * 70)
        
        # 統一測試密碼
        test_password = "test123"
        password_hash = generate_password_hash(test_password)
        
        account_list = []
        
        for idx, user in enumerate(users, 1):
            print(f"{idx:<4} {user.email:<40} {user.name or user.nickname or 'N/A':<20}")
            
            # 重置密碼
            user.password_hash = password_hash
            
            account_list.append({
                '編號': idx,
                '郵箱': user.email,
                '名稱': user.name or user.nickname or 'N/A',
                '密碼': test_password
            })
        
        # 提交所有密碼更改
        db.session.commit()
        
        print("=" * 70)
        print(f"\n✓ 所有 {len(users)} 個帳號的密碼已重置為: {test_password}")
        print("\n完整帳號列表：")
        print("=" * 70)
        
        for acc in account_list:
            print(f"{acc['編號']}. 郵箱: {acc['郵箱']}")
            print(f"   名稱: {acc['名稱']}")
            print(f"   密碼: {acc['密碼']}")
            print("-" * 70)

if __name__ == "__main__":
    list_and_reset_passwords()
