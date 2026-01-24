"""
為所有現有帳號生成測試數據腳本
時間範圍：2025/11/1 到 2026/1/3
分數特性：大幅度起伏（使用全範圍0-56）
每天3次評估
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

def generate_varied_answers():
    """生成有大幅度變化的問卷答案"""
    questions = 14
    answers = []
    total_score = 0
    
    # 使用不同的策略產生大幅度變化
    strategy = random.choice(['low', 'medium', 'high', 'mixed'])
    
    if strategy == 'low':
        # 低分段：大部分0-1分
        score_range = [0, 0, 0, 1, 1, 2]
    elif strategy == 'high':
        # 高分段：大部分3-4分
        score_range = [2, 3, 3, 4, 4, 4]
    elif strategy == 'medium':
        # 中分段：大部分1-3分
        score_range = [1, 1, 2, 2, 3, 3]
    else:
        # 混合：完全隨機
        score_range = [0, 1, 2, 3, 4]
    
    for i in range(questions):
        score = random.choice(score_range)
        answers.append({
            "question": i + 1,
            "score": score
        })
        total_score += score
    
    return answers, total_score

def populate_all_accounts():
    """為所有帳號填充測試數據"""
    app = create_app()
    
    with app.app_context():
        # 獲取所有用戶
        users = User.query.all()
        
        if not users:
            print("沒有找到任何用戶！")
            return
        
        print(f"找到 {len(users)} 個用戶帳號")
        print("=" * 60)
        
        # 設定時間範圍
        start_date = datetime(2025, 11, 1)
        end_date = datetime(2026, 1, 3)
        times = [
            (9, 0),   # 早上9點
            (15, 0),  # 下午3點
            (21, 0)   # 晚上9點
        ]
        
        expected_days = (end_date - start_date).days + 1
        expected_records_per_user = expected_days * len(times)
        
        print(f"時間範圍: {start_date.date()} 至 {end_date.date()}")
        print(f"預計天數: {expected_days} 天")
        print(f"每日次數: {len(times)} 次")
        print(f"每個用戶預計記錄數: {expected_records_per_user} 筆")
        print("=" * 60)
        
        for user_idx, user in enumerate(users, 1):
            print(f"\n處理用戶 {user_idx}/{len(users)}: {user.email}")
            
            # 刪除該用戶現有的評估記錄
            existing_records = AssessmentHistory.query.filter_by(user_id=user.id).all()
            if existing_records:
                print(f"  清除現有的 {len(existing_records)} 筆記錄...")
                for record in existing_records:
                    db.session.delete(record)
                db.session.commit()
            
            # 生成新記錄
            current_date = start_date
            record_count = 0
            
            while current_date <= end_date:
                for hour, minute in times:
                    completed_time = datetime(
                        current_date.year,
                        current_date.month,
                        current_date.day,
                        hour,
                        minute,
                        0
                    )
                    
                    # 生成有大幅度變化的答案和分數
                    answers, total_score = generate_varied_answers()
                    max_score = 56
                    
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
                
                current_date += timedelta(days=1)
            
            # 提交該用戶的所有記錄
            db.session.commit()
            print(f"  ✓ 完成！生成 {record_count} 筆記錄")
        
        print("\n" + "=" * 60)
        print(f"✓ 全部完成！")
        print(f"  處理用戶數: {len(users)}")
        print(f"  每個用戶記錄數: {expected_records_per_user}")
        print(f"  總記錄數: {len(users) * expected_records_per_user}")
        print(f"\n所有帳號現在都有從 {start_date.date()} 到 {end_date.date()} 的測試數據！")
        print(f"分數設計為大幅度起伏，範圍涵蓋 0-56 分。")

if __name__ == "__main__":
    populate_all_accounts()
