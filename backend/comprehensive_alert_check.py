"""
全面檢查所有帳號的1月5日警報狀態
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import User, ScoreAlert, AssessmentHistory
from app.utils.alert_utils import calculate_daily_average
from datetime import datetime, date
import json

app = create_app()

# 目標測試帳號
target_emails = [
    'test_manual@gmail.com',      # Test Manual
    'angel921030chen@gmail.com',  # 123
    '111025015@live.asia.edu.tw', # xian
    'test_update@example.com',    # Tester
    '111025048@live.asia.edu.tw'  # 唐洋雞
]

jan5 = date(2026, 1, 5)
jan6 = date(2026, 1, 6)

with app.app_context():
    print("=" * 80)
    print("1. 檢查5個目標帳號的1月5日警報狀態")
    print("=" * 80)
    
    for email in target_emails:
        user = User.query.filter_by(email=email).first()
        if not user:
            print(f"❌ 找不到帳號: {email}")
            continue
        
        # 檢查1月5日的評估記錄（使用completed_at範圍查詢）
        assessments = AssessmentHistory.query.filter(
            AssessmentHistory.user_id == user.id,
            AssessmentHistory.completed_at >= datetime.combine(jan5, datetime.min.time()),
            AssessmentHistory.completed_at < datetime.combine(jan6, datetime.min.time())
        ).all()
        
        # 檢查1月5日的警報
        alerts = ScoreAlert.query.filter_by(
            user_id=user.id,
            alert_date=jan5,
            is_read=False
        ).all()
        
        high_alerts = [a for a in alerts if a.alert_type == 'high']
        low_alerts = [a for a in alerts if a.alert_type == 'low']
        
        print(f"\n📧 {user.name} ({email})")
        print(f"   評估記錄數: {len(assessments)}")
        if assessments:
            scores = [f"{a.total_score}/{a.max_score}" for a in assessments]
            print(f"   分數: {scores}")
            
            # 計算當日平均
            daily_avg, count = calculate_daily_average(user.id, jan5)
            if daily_avg:
                print(f"   當日平均: {daily_avg:.2f}")
        
        print(f"   警報: 高={len(high_alerts)}, 低={len(low_alerts)}")
        for alert in high_alerts:
            try:
                lines = json.loads(alert.exceeded_lines)
                line_names = list(lines.keys())
                print(f"      ⚠️  [HIGH] 穿越: {', '.join(line_names)}")
            except:
                print(f"      ⚠️  [HIGH] {alert.exceeded_lines}")
                
        for alert in low_alerts:
            try:
                lines = json.loads(alert.exceeded_lines)
                line_names = list(lines.keys())
                print(f"      ⚠️  [LOW] 接近: {', '.join(line_names)}")
            except:
                print(f"      ⚠️  [LOW] {alert.exceeded_lines}")
        
        if len(high_alerts) == 0 and len(low_alerts) == 0:
            print(f"   ⚠️  沒有警報！")
    
    print("\n" + "=" * 80)
    print("2. 檢查其他帳號是否有1月5日的評估記錄")
    print("=" * 80)
    
    all_users = User.query.all()
    other_users_with_jan5_data = []
    
    for user in all_users:
        if user.email in target_emails:
            continue
        
        # 檢查是否有1月5日的評估記錄
        jan5_assessments = AssessmentHistory.query.filter(
            AssessmentHistory.user_id == user.id,
            AssessmentHistory.completed_at >= datetime.combine(jan5, datetime.min.time()),
            AssessmentHistory.completed_at < datetime.combine(jan6, datetime.min.time())
        ).count()
        
        if jan5_assessments > 0:
            other_users_with_jan5_data.append({
                'user': user,
                'count': jan5_assessments
            })
    
    if other_users_with_jan5_data:
        print(f"\n⚠️  發現 {len(other_users_with_jan5_data)} 個非測試帳號有1月5日的評估記錄:")
        for item in other_users_with_jan5_data:
            user = item['user']
            count = item['count']
            print(f"   - {user.name} ({user.email}): {count} 筆記錄")
    else:
        print("\n✅ 沒有其他帳號有1月5日的評估記錄")
    
    print("\n" + "=" * 80)
    print("3. 檢查所有目標帳號的未讀警報總數")
    print("=" * 80)
    
    for email in target_emails:
        user = User.query.filter_by(email=email).first()
        if not user:
            continue
        
        unread_alerts = ScoreAlert.query.filter_by(
            user_id=user.id,
            is_read=False
        ).order_by(ScoreAlert.alert_date.desc()).all()
        
        print(f"\n📧 {user.name}:")
        print(f"   未讀警報總數: {len(unread_alerts)}")
        
        # 列出所有未讀警報的日期和類型
        for alert in unread_alerts[:5]:  # 只顯示前5個
            try:
                lines = json.loads(alert.exceeded_lines)
                line_names = list(lines.keys())
                action = "穿越" if alert.alert_type == 'high' else "接近"
                print(f"   - {alert.alert_date} [{alert.alert_type}] {action}: {', '.join(line_names)}")
            except:
                print(f"   - {alert.alert_date} [{alert.alert_type}]")
        
        if len(unread_alerts) > 5:
            print(f"   ... 還有 {len(unread_alerts) - 5} 個警報")
