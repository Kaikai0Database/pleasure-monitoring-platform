"""
詳細分析 expert test 數據的移動平均線
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.models import User, AssessmentHistory
from datetime import datetime, date, timedelta
from sqlalchemy import func
from collections import defaultdict

app = create_app()

def calculate_daily_averages(user_id, start_date, end_date):
    """計算每日平均分數"""
    daily_scores = defaultdict(list)
    
    # 獲取所有評估記錄
    assessments = AssessmentHistory.query.filter(
        AssessmentHistory.user_id == user_id,
        func.date(AssessmentHistory.completed_at) >= start_date,
        func.date(AssessmentHistory.completed_at) <= end_date
    ).order_by(AssessmentHistory.completed_at).all()
    
    # 按日期分組
    for assessment in assessments:
        assessment_date = assessment.completed_at.date()
        daily_scores[assessment_date].append(assessment.total_score)
    
    # 計算每日平均
    daily_data = []
    current_date = start_date
    while current_date <= end_date:
        if current_date in daily_scores:
            avg = sum(daily_scores[current_date]) / len(daily_scores[current_date])
            daily_data.append({
                'date': current_date,
                'avg': avg,
                'count': len(daily_scores[current_date])
            })
        current_date += timedelta(days=1)
    
    return daily_data

def calculate_moving_average(daily_data, window):
    """計算移動平均"""
    if len(daily_data) < window:
        return None
    
    scores = [d['avg'] for d in daily_data[-window:]]
    return sum(scores) / len(scores)

with app.app_context():
    users = User.query.filter(User.email.in_(['experttest1@example.com', 'experttest2@example.com'])).all()
    
    start_date = date(2025, 12, 1)
    end_date = date(2026, 2, 1)
    
    print("="*80)
    print("Expert Test 移動平均線詳細分析")
    print("="*80)
    
    for user in users:
        print(f"\n{'='*60}")
        print(f"用戶: {user.name} ({user.email})")
        print(f"{'='*60}")
        
        # 獲取每日平均數據
        daily_data = calculate_daily_averages(user.id, start_date, end_date)
        
        if not daily_data:
            print("❌ 無數據")
            continue
        
        print(f"\n總天數: {len(daily_data)} 天")
        print(f"日期範圍: {daily_data[0]['date']} 至 {daily_data[-1]['date']}")
        
        # 計算最後一天的移動平均
        last_day = daily_data[-1]
        ma_7 = calculate_moving_average(daily_data, 7)
        ma_14 = calculate_moving_average(daily_data, 14)
        ma_30 = calculate_moving_average(daily_data, 30)
        
        print(f"\n最後一天 ({last_day['date']}) 數據:")
        print(f"  日平均分數: {last_day['avg']:.2f}")
        print(f"  評估次數: {last_day['count']}")
        
        print(f"\n移動平均線:")
        print(f"  7日移動平均: {ma_7:.2f}")
        print(f"  14日移動平均: {ma_14:.2f}")
        print(f"  30日移動平均: {ma_30:.2f}")
        
        # 分析穿越和接近情況
        print(f"\n穿越分析:")
        crossed = []
        if last_day['avg'] > ma_7:
            diff = last_day['avg'] - ma_7
            crossed.append(f"  ✅ 超越 7日線 ({last_day['avg']:.2f} > {ma_7:.2f}, 差距 {diff:.2f})")
        else:
            diff = ma_7 - last_day['avg']
            crossed.append(f"  ❌ 未超越 7日線 ({last_day['avg']:.2f} < {ma_7:.2f}, 差距 {diff:.2f})")
        
        if last_day['avg'] > ma_14:
            diff = last_day['avg'] - ma_14
            crossed.append(f"  ✅ 超越 14日線 ({last_day['avg']:.2f} > {ma_14:.2f}, 差距 {diff:.2f})")
        else:
            diff = ma_14 - last_day['avg']
            crossed.append(f"  ❌ 未超越 14日線 ({last_day['avg']:.2f} < {ma_14:.2f}, 差距 {diff:.2f})")
        
        if last_day['avg'] > ma_30:
            diff = last_day['avg'] - ma_30
            crossed.append(f"  ✅ 超越 30日線 ({last_day['avg']:.2f} > {ma_30:.2f}, 差距 {diff:.2f})")
        else:
            diff = ma_30 - last_day['avg']
            crossed.append(f"  ❌ 未超越 30日線 ({last_day['avg']:.2f} < {ma_30:.2f}, 差距 {diff:.2f})")
        
        for line in crossed:
            print(line)
        
        # 接近分析（差距 < 2分）
        print(f"\n接近分析 (差距 < 2分):")
        approaching = []
        
        diff_7 = abs(last_day['avg'] - ma_7)
        if diff_7 < 2:
            approaching.append(f"  ✅ 接近 7日線 (差距 {diff_7:.2f})")
        
        diff_14 = abs(last_day['avg'] - ma_14)
        if diff_14 < 2:
            approaching.append(f"  ✅ 接近 14日線 (差距 {diff_14:.2f})")
        
        diff_30 = abs(last_day['avg'] - ma_30)
        if diff_30 < 2:
            approaching.append(f"  ✅ 接近 30日線 (差距 {diff_30:.2f})")
        
        if approaching:
            for line in approaching:
                print(line)
        else:
            print("  ❌ 未接近任何移動平均線（所有差距 >= 2分）")
        
        # 顯示最近10天的詳細數據
        print(f"\n最近 10 天詳細數據:")
        print(f"{'日期':<12} {'日平均':<8} {'評估次數':<8}")
        print("-" * 30)
        for day in daily_data[-10:]:
            print(f"{day['date']!s:<12} {day['avg']:>7.2f} {day['count']:>8}")
    
    print(f"\n{'='*80}")
    print("分析完成")
    print(f"{'='*80}")
