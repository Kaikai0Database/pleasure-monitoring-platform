"""
為 experttest1 和 experttest2 創建測驗數據
日期範圍：2025/12/1 到 2026/02/01
每天 3 次測驗：早上 8:00、下午 14:00、晚上 20:00
最後一天的日平均要超越並接近移動平均線
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.models import User, AssessmentHistory
from datetime import datetime, timedelta
import random
import json

app = create_app()

# 測試帳號資訊
ACCOUNTS = [
    {
        'email': 'experttest1@example.com',
        'name': '專家測試1',
        'nickname': 'Expert Test 1',
        'group': 'clinical'
    },
    {
        'email': 'experttest2@example.com',
        'name': '專家測試2',
        'nickname': 'Expert Test 2',
        'group': 'clinical'
    }
]

# 時間設定
START_DATE = datetime(2025, 12, 1, 8, 0, 0)
END_DATE = datetime(2026, 2, 1, 20, 0, 0)
TIMES_PER_DAY = [8, 14, 20]  # 早上8點、下午2點、晚上8點

def calculate_moving_average(scores, window):
    """計算移動平均"""
    if len(scores) < window:
        return None
    return sum(scores[-window:]) / window

def generate_sample_answers(target_score):
    """生成樣本答案，確保總分接近目標分數"""
    # 14題，每題0-4分
    answers = []
    remaining = target_score
    
    for i in range(14):
        if i == 13:  # 最後一題
            score = min(4, max(0, remaining))
        else:
            # 隨機分配，但確保不超過剩餘分數
            max_score = min(4, remaining - (13 - i))  # 確保後面還有分數
            score = random.randint(0, max_score)
        
        answers.append({
            "questionId": i + 1,
            "emoji": f"emoji_{i+1}",
            "score": score
        })
        remaining -= score
    
    return answers

def design_score_pattern():
    """
    設計分數模式，確保最後一天：
    1. 日平均線超越「一條」移動平均線（產生「超越」警報）
    2. 日平均線接近「另一條」移動平均線（產生「接近」警報）
    
    策略：
    - 前期（12月1-20日）：分數在 30-34 之間波動
    - 中期（12月21日-1月10日）：分數逐漸下降到 25-27
    - 低谷期（1月11-25日）：維持在 24-26
    - 回升期（1月26-31日）：緩慢上升到 27-28
    - 最後一天（2月1日）：穩定在 28-29
    
    預期最後一天結果：
    - 7日移動平均：~27（最後一週緩慢上升）
    - 14日移動平均：~26-27（包含部分低谷期）
    - 30日移動平均：~29-30（包含高分期）
    - 最後一天日平均：28-29
    
    效果：
    - 超越 7日線和14日線（28-29 > 27）✅
    - 接近 30日線（|28-29 - 30| < 2）✅
    """
    
    total_days = (END_DATE.date() - START_DATE.date()).days + 1
    scores = []
    
    for day_index in range(total_days):
        current_date = START_DATE.date() + timedelta(days=day_index)
        
        # 12月1-20日（前20天）：中等偏高
        if day_index < 20:
            base_score = 32
            variation = random.randint(-2, 2)
        # 12月21日-1月10日（第21-41天）：逐漸下降
        elif day_index < 41:
            progress = (day_index - 20) / 21
            base_score = int(32 - progress * 7)  # 從32降到25
            variation = random.randint(-1, 1)
        # 1月11-25日（第42-56天）：低谷期
        elif day_index < 56:
            base_score = 25
            variation = random.randint(-1, 1)
        # 1月26-31日（第57-62天）：緩慢回升
        elif day_index < total_days - 1:
            days_from_start_recovery = day_index - 56
            base_score = 25 + days_from_start_recovery * 0.5  # 每天上升0.5分
            variation = random.randint(-1, 1)
        # 最後一天（2月1日，第63天）：穩定在28-29
        else:
            base_score = 28
            variation = random.randint(0, 1)
        
        final_score = int(base_score + variation)
        final_score = max(15, min(50, final_score))  # 限制在15-50之間
        
        scores.append({
            'date': current_date,
            'score': final_score
        })
    
    return scores

def create_assessments_for_user(user, score_pattern):
    """為指定用戶創建評估記錄"""
    print(f"\n{'='*60}")
    print(f"為用戶創建評估記錄: {user.name} ({user.email})")
    print(f"{'='*60}")
    
    # 刪除舊記錄
    old_assessments = AssessmentHistory.query.filter_by(user_id=user.id).all()
    for assessment in old_assessments:
        db.session.delete(assessment)
    db.session.commit()
    print(f"[DELETE] 刪除了 {len(old_assessments)} 條舊記錄")
    
    # 創建新記錄
    assessments_created = 0
    current_date = START_DATE
    
    for day_pattern in score_pattern:
        target_date = day_pattern['date']
        target_score = day_pattern['score']
        
        # 每天3次測驗
        for hour in TIMES_PER_DAY:
            assessment_time = datetime.combine(target_date, datetime.min.time()) + timedelta(hours=hour)
            
            # 為每次測驗生成略微不同的分數（±2分）
            actual_score = target_score + random.randint(-2, 2)
            actual_score = max(5, min(56, actual_score))
            
            # 確定等級
            level = '需要關注' if actual_score >= 30 else '良好'
            
            # 生成答案
            answers = generate_sample_answers(actual_score)
            
            # 創建評估記錄
            assessment = AssessmentHistory(
                user_id=user.id,
                total_score=actual_score,
                max_score=56,
                level=level,
                answers=json.dumps(answers),
                completed_at=assessment_time
            )
            db.session.add(assessment)
            assessments_created += 1
    
    db.session.commit()
    print(f"[OK] 創建了 {assessments_created} 條評估記錄")
    
    # 計算並顯示統計信息
    display_statistics(user, score_pattern)

def display_statistics(user, score_pattern):
    """顯示統計信息"""
    print(f"\n{'='*60}")
    print(f"統計信息: {user.name}")
    print(f"{'='*60}")
    
    # 計算每日平均分數列表
    daily_averages = [p['score'] for p in score_pattern]
    
    # 計算最後一天的移動平均
    last_day_avg = daily_averages[-1]
    
    # 計算7日、14日、30日移動平均（基於最後一天）
    ma_7 = calculate_moving_average(daily_averages, 7)
    ma_14 = calculate_moving_average(daily_averages, 14)
    ma_30 = calculate_moving_average(daily_averages, 30)
    
    print(f"日期範圍: {score_pattern[0]['date']} 至 {score_pattern[-1]['date']}")
    print(f"總天數: {len(score_pattern)} 天")
    print(f"總評估次數: {len(score_pattern) * 3} 次")
    print(f"\n最後一天 (2026/02/01) 數據:")
    print(f"  日平均分數: {last_day_avg:.1f}")
    print(f"  7日移動平均: {ma_7:.1f}")
    print(f"  14日移動平均: {ma_14:.1f}")
    print(f"  30日移動平均: {ma_30:.1f}")
    
    # 檢查是否滿足條件
    print(f"\n警報條件檢查:")
    
    # 超越檢查
    exceeds = []
    if last_day_avg > ma_7:
        exceeds.append(f"7日線 ({last_day_avg:.1f} > {ma_7:.1f})")
    if last_day_avg > ma_14:
        exceeds.append(f"14日線 ({last_day_avg:.1f} > {ma_14:.1f})")
    if last_day_avg > ma_30:
        exceeds.append(f"30日線 ({last_day_avg:.1f} > {ma_30:.1f})")
    
    if exceeds:
        print(f"  ✅ 超越: {', '.join(exceeds)}")
    else:
        print(f"  ❌ 未超越任何移動平均線")
    
    # 接近檢查（差距 < 2分）
    approaching = []
    if abs(last_day_avg - ma_7) < 2 and last_day_avg <= ma_7:
        approaching.append(f"7日線 (差距 {abs(last_day_avg - ma_7):.1f})")
    if abs(last_day_avg - ma_14) < 2 and last_day_avg <= ma_14:
        approaching.append(f"14日線 (差距 {abs(last_day_avg - ma_14):.1f})")
    if abs(last_day_avg - ma_30) < 2 and last_day_avg <= ma_30:
        approaching.append(f"30日線 (差距 {abs(last_day_avg - ma_30):.1f})")
    
    if approaching:
        print(f"  ✅ 接近: {', '.join(approaching)}")
    else:
        print(f"  ⚠️  未接近任何移動平均線（可能已超越）")

def main():
    """主函數"""
    print("="*80)
    print("為 experttest1 和 experttest2 創建測驗數據")
    print("="*80)
    print(f"日期範圍: {START_DATE.date()} 至 {END_DATE.date()}")
    print(f"每天測驗次數: 3 次 (8:00, 14:00, 20:00)")
    print()
    
    with app.app_context():
        # 設計分數模式
        print("[INFO] 設計分數模式...")
        score_pattern = design_score_pattern()
        print(f"[OK] 生成了 {len(score_pattern)} 天的分數模式")
        
        # 為每個帳號創建或更新用戶並生成評估
        from werkzeug.security import generate_password_hash
        
        for account_info in ACCOUNTS:
            # 檢查用戶是否存在
            user = User.query.filter_by(email=account_info['email']).first()
            
            if not user:
                # 創建新用戶
                user = User(
                    email=account_info['email'],
                    name=account_info['name'],
                    nickname=account_info['nickname'],
                    password_hash=generate_password_hash('test123'),
                    group=account_info['group'],
                    created_at=START_DATE - timedelta(days=10)
                )
                db.session.add(user)
                db.session.commit()
                print(f"\n[CREATE] 創建新用戶: {user.name} (ID: {user.id})")
            else:
                print(f"\n[EXISTS] 用戶已存在: {user.name} (ID: {user.id})")
            
            # 為用戶創建評估記錄
            create_assessments_for_user(user, score_pattern)
        
        print(f"\n{'='*80}")
        print("✅ 所有數據創建完成！")
        print(f"{'='*80}")
        print("\n測試帳號登入資訊:")
        print("  帳號1: experttest1@example.com / test123")
        print("  帳號2: experttest2@example.com / test123")
        print("\n請在管理後台查看這兩個帳號的圖表數據")
        print("預期在 2026/02/01 會觸發警報（超越並接近移動平均線）")

if __name__ == '__main__':
    main()
