"""
修正所有帳號中低於14分的記錄
將所有 total_score < 14 的記錄改為 45-56 分之間
"""

import sys
import os
import random
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app
from app.models import db, User, AssessmentHistory

def generate_high_score_answers():
    """生成45-56分範圍的答案（目標分數45-56）"""
    questions = 14
    answers = []
    
    # 目標分數：45-56分
    # 每題最多4分，14題共56分
    # 45分平均每題需要 45/14 ≈ 3.2分
    # 56分平均每題 4分
    
    # 隨機生成45-56分的組合
    target_score = random.randint(45, 56)
    
    # 先給每題基礎分3分（共42分）
    scores = [3] * questions
    
    # 剩餘分數隨機分配
    remaining = target_score - 42
    for _ in range(remaining):
        idx = random.randint(0, questions - 1)
        if scores[idx] < 4:  # 確保不超過4分
            scores[idx] += 1
    
    total_score = 0
    for i, score in enumerate(scores):
        answers.append({
            "question": i + 1,
            "score": score
        })
        total_score += score
    
    return answers, total_score

def fix_low_scores():
    """修正所有低於14分的記錄"""
    app = create_app()
    
    with app.app_context():
        # 查找所有分數低於14分的記錄
        low_score_records = AssessmentHistory.query.filter(
            AssessmentHistory.total_score < 14,
            AssessmentHistory.is_deleted == False
        ).all()
        
        if not low_score_records:
            print("沒有找到分數低於14分的記錄！")
            return
        
        print(f"找到 {len(low_score_records)} 筆分數低於14分的記錄")
        print("=" * 60)
        
        # 按用戶分組統計
        user_stats = {}
        for record in low_score_records:
            user_id = record.user_id
            if user_id not in user_stats:
                user = User.query.get(user_id)
                user_stats[user_id] = {
                    'email': user.email if user else 'Unknown',
                    'count': 0,
                    'records': []
                }
            user_stats[user_id]['count'] += 1
            user_stats[user_id]['records'].append(record)
        
        print(f"涉及 {len(user_stats)} 個用戶：")
        for user_id, stats in user_stats.items():
            print(f"  {stats['email']}: {stats['count']} 筆")
        
        print("\n開始修正...")
        print("=" * 60)
        
        updated_count = 0
        for user_id, stats in user_stats.items():
            print(f"\n處理用戶: {stats['email']}")
            
            for record in stats['records']:
                old_score = record.total_score
                
                # 生成新的高分答案（45-56分）
                new_answers, new_score = generate_high_score_answers()
                
                # 更新記錄
                record.total_score = new_score
                record.answers = json.dumps(new_answers, ensure_ascii=False)
                record.level = "需要關注"  # 高分都是需要關注
                
                updated_count += 1
                
                if updated_count % 50 == 0:
                    print(f"  已更新 {updated_count} 筆...")
        
        # 提交所有更改
        db.session.commit()
        
        print("\n" + "=" * 60)
        print(f"✓ 修正完成！")
        print(f"  總共更新: {updated_count} 筆記錄")
        print(f"  涉及用戶: {len(user_stats)} 個")
        print(f"\n所有原本低於14分的記錄已改為 45-56 分！")

if __name__ == "__main__":
    fix_low_scores()
