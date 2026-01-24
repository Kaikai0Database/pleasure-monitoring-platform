"""
檢查非目標帳號的警報狀態
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import User, ScoreAlert, AssessmentHistory, db
from app.utils.alert_utils import calculate_daily_average
from datetime import datetime, date
import json

app = create_app()

target_emails = [
    'test_manual@gmail.com',
    'angel921030chen@gmail.com',
    '111025015@live.asia.edu.tw',
    'test_update@example.com',
    '111025048@live.asia.edu.tw'
]

output_lines = []

with app.app_context():
    output_lines.append("檢查非目標帳號的警報狀態")
    output_lines.append("=" * 80)
    
    all_users = User.query.all()
    
    users_without_alerts = []
    users_with_alerts = []
    
    for user in all_users:
        if user.email in target_emails:
            continue
        
        # 檢查未讀警報
        unread_alerts = ScoreAlert.query.filter_by(
            user_id=user.id,
            is_read=False
        ).order_by(ScoreAlert.alert_date.desc()).all()
        
        # 檢查最新的評估記錄
        latest_assessment = AssessmentHistory.query.filter_by(
            user_id=user.id
        ).order_by(AssessmentHistory.completed_at.desc()).first()
        
        if latest_assessment:
            latest_date = latest_assessment.completed_at.date()
            
            if len(unread_alerts) == 0:
                users_without_alerts.append({
                    'user': user,
                    'latest_date': latest_date
                })
            else:
                users_with_alerts.append({
                    'user': user,
                    'alert_count': len(unread_alerts),
                    'latest_alert_date': unread_alerts[0].alert_date
                })
    
    output_lines.append(f"\n有未讀警報的帳號: {len(users_with_alerts)}")
    for item in users_with_alerts[:10]:
        user = item['user']
        output_lines.append(f"  ✓ {user.name} ({user.email}): {item['alert_count']} 個警報, 最新: {item['latest_alert_date']}")
    
    output_lines.append(f"\n沒有未讀警報的帳號: {len(users_without_alerts)}")
    for item in users_without_alerts[:20]:
        user = item['user']
        output_lines.append(f"  ✗ {user.name} ({user.email}): 最新評估 {item['latest_date']}")
    
    if len(users_without_alerts) > 20:
        output_lines.append(f"  ... 還有 {len(users_without_alerts) - 20} 個帳號")

# Write to file and print
with open('other_users_alert_status.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output_lines))

print("Output written to other_users_alert_status.txt")
for line in output_lines:
    print(line)
