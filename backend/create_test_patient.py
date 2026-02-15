"""
測試數據生成腳本
創建一個新的病人帳戶，並生成從 2024/11/1 到 2024/12/2 的評估記錄
每天生成 3 筆記錄（早上9點、下午3點、晚上9點）
"""

import sys
import os
from datetime import datetime, timedelta
import random
import json

# 添加項目路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app
from app.models import db, User, AssessmentHistory
from werkzeug.security import generate_password_hash

def generate_random_answers():
    """生成隨機的問卷答案"""
    # 14題，每題0-4分
    questions = 14
    answers = []
    total_score = 0
    
    for i in range(questions):
        # 隨機生成0-4分的答案
        score = random.randint(0, 4)
        answers.append({
            "question": i + 1,
            "score": score
        })
        total_score += score
    
    return answers, total_score

def create_test_patient():
    """創建測試病人帳戶"""
    app = create_app()
    
    with app.app_context():
        # 檢查用戶是否已存在
        email = "test_patient@example.com"
        existing_user = User.query.filter_by(email=email).first()
        
        if existing_user:
            print(f"✓ 用戶已存在: {email} (ID: {existing_user.id})")
            user = existing_user
        else:
            # 創建新用戶
            user = User(
                email=email,
                name="測試病患",
                password_hash=generate_password_hash("test123"),
                nickname="測試病患",
                is_profile_completed=True,
                created_at=datetime(2024, 10, 25)  # 在11/1之前創建帳戶
            )
            db.session.add(user)
            db.session.commit()
            print(f"✓ 創建新用戶: {email} (ID: {user.id})")
        
        # 刪除該用戶現有的評估記錄（如果要重新生成）
        existing_records = AssessmentHistory.query.filter_by(user_id=user.id).all()
        if existing_records:
            print(f"  清除現有的 {len(existing_records)} 筆評估記錄...")
            for record in existing_records:
                db.session.delete(record)
            db.session.commit()
        
        # 生成評估記錄
        start_date = datetime(2024, 11, 1)
        end_date = datetime(2024, 12, 2)
        times = [
            (9, 0),   # 早上9點
            (15, 0),  # 下午3點
            (21, 0)   # 晚上9點
        ]
        
        current_date = start_date
        record_count = 0
        
        print(f"\n開始生成評估記錄...")
        print(f"時間範圍: {start_date.date()} 至 {end_date.date()}")
        print(f"每日次數: {len(times)} 次")
        print("-" * 50)
        
        while current_date <= end_date:
            for hour, minute in times:
                # 設定具體時間
                completed_time = datetime(
                    current_date.year,
                    current_date.month,
                    current_date.day,
                    hour,
                    minute,
                    0
                )
                
                # 生成隨機答案和分數
                answers, total_score = generate_random_answers()
                max_score = 56  # 14題 × 4分
                
                # 根據分數決定等級
                if total_score >= 24:
                    level = "需要關注"
                else:
                    level = "良好"
                
                # 創建評估記錄
                assessment = AssessmentHistory(
                    user_id=user.id,
                    total_score=total_score,
                    max_score=max_score,
                    level=level,
                    answers=json.dumps(answers, ensure_ascii=False),
                    completed_at=completed_time,
                    is_deleted=False
                )
                
                db.session.add(assessment)
                record_count += 1
                
                # 每10筆記錄輸出一次進度
                if record_count % 10 == 0:
                    print(f"  已生成 {record_count} 筆記錄...")
            
            # 移到下一天
            current_date += timedelta(days=1)
        
        # 提交所有記錄
        db.session.commit()
        
        print("-" * 50)
        print(f"✓ 完成！共生成 {record_count} 筆評估記錄")
        print(f"\n帳戶資訊:")
        print(f"  郵箱: {email}")
        print(f"  密碼: test123")
        print(f"  用戶ID: {user.id}")
        print(f"\n記錄摘要:")
        print(f"  時間範圍: {start_date.date()} 至 {end_date.date()}")
        print(f"  總天數: {(end_date - start_date).days + 1} 天")
        print(f"  總記錄數: {record_count} 筆")
        print(f"\n您現在可以使用此帳戶登入測試當日圖表功能！")

if __name__ == "__main__":
    create_test_patient()
