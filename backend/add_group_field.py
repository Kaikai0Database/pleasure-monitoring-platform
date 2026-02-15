"""
添加 group 欄位到 users 表並標記大學生組病人
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app
from app.models import db, User

def add_group_field():
    """添加group欄位並標記病人"""
    app = create_app()
    
    with app.app_context():
        # 添加欄位的SQL（如果不存在）
        try:
            db.session.execute(db.text(
                "ALTER TABLE users ADD COLUMN `group` VARCHAR(20) DEFAULT 'clinical'"
            ))
            db.session.commit()
            print("✓ 已添加 group 欄位到 users 表")
        except Exception as e:
            if "duplicate column name" in str(e).lower() or "已經存在" in str(e).lower():
                print("⚠ group 欄位已存在，跳過創建")
                db.session.rollback()
            else:
                print(f"✗ 添加欄位失敗: {str(e)}")
                db.session.rollback()
                return
        
        # 所有病人初始設為臨床組
        all_users = User.query.all()
        for user in all_users:
            if not user.group:
                user.group = 'clinical'
        db.session.commit()
        print(f"✓ 已將 {len(all_users)} 個病人設為臨床組")
        
        # 大學生組成員名單（根據 nickname 或 name）
        student_names = ['唐洋雞', '大帥哥', 'xian', '12345', '123']
        
        print(f"\n開始標記大學生組...")
        print("=" * 60)
        
        marked_count = 0
        for name in student_names:
            users = User.query.filter(
                (User.nickname == name) | (User.name == name)
            ).all()
            
            if users:
                for user in users:
                    user.group = 'student'
                    marked_count += 1
                    print(f"✓ 標記為大學生組: {user.nickname or user.name} ({user.email})")
            else:
                print(f"⚠ 找不到病人: {name}")
        
        db.session.commit()
        
        print("=" * 60)
        print(f"✓ 完成！共標記 {marked_count} 個病人為大學生組")
        
        # 顯示統計
        student_count = User.query.filter_by(group='student').count()
        clinical_count = User.query.filter_by(group='clinical').count()
        
        print(f"\n病人分組統計:")
        print(f"  大學生組: {student_count} 人")
        print(f"  臨床組: {clinical_count} 人")
        print(f"  總計: {student_count + clinical_count} 人")

if __name__ == "__main__":
    add_group_field()
