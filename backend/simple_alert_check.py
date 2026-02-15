"""
簡化的警報檢查 - 直接輸出到檔案
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

target_emails = [
    'test_manual@gmail.com',
    'angel921030chen@gmail.com',
    '111025015@live.asia.edu.tw',
    'test_update@example.com',
    '111025048@live.asia.edu.tw'
]

jan5 = date(2026, 1, 5)
jan6 = date(2026, 1, 6)

output_lines = []

with app.app_context():
    output_lines.append("=" * 80)
    output_lines.append("1. Check target users January 5 alerts")
    output_lines.append("=" * 80)
    
    for email in target_emails:
        user = User.query.filter_by(email=email).first()
        if not user:
            output_lines.append(f"NOT FOUND: {email}")
            continue
        
        # Check Jan 5 assessments
        assessments = AssessmentHistory.query.filter(
            AssessmentHistory.user_id == user.id,
            AssessmentHistory.completed_at >= datetime.combine(jan5, datetime.min.time()),
            AssessmentHistory.completed_at < datetime.combine(jan6, datetime.min.time())
        ).all()
        
        # Check Jan 5 alerts
        alerts = ScoreAlert.query.filter_by(
            user_id=user.id,
            alert_date=jan5,
            is_read=False
        ).all()
        
        high_alerts = [a for a in alerts if a.alert_type == 'high']
        low_alerts = [a for a in alerts if a.alert_type == 'low']
        
        output_lines.append(f"\nUser: {user.name} ({email})")
        output_lines.append(f"  Assessments on Jan 5: {len(assessments)}")
        
        if assessments:
            scores = [f"{a.total_score}/{a.max_score}" for a in assessments]
            output_lines.append(f"  Scores: {', '.join(scores)}")
            daily_avg, count = calculate_daily_average(user.id, jan5)
            if daily_avg:
                output_lines.append(f"  Daily Average: {daily_avg:.2f}")
        
        output_lines.append(f"  Alerts: HIGH={len(high_alerts)}, LOW={len(low_alerts)}")
        
        for alert in high_alerts:
            try:
                lines = json.loads(alert.exceeded_lines)
                line_names = list(lines.keys())
                output_lines.append(f"    [HIGH] Cross over: {', '.join(line_names)}")
            except:
                output_lines.append(f"    [HIGH] {alert.exceeded_lines}")
                
        for alert in low_alerts:
            try:
                lines = json.loads(alert.exceeded_lines)
                line_names = list(lines.keys())
                output_lines.append(f"    [LOW] Approaching: {', '.join(line_names)}")
            except:
                output_lines.append(f"    [LOW] {alert.exceeded_lines}")
        
        if len(high_alerts) == 0 and len(low_alerts) == 0:
            output_lines.append(f"    NO ALERTS!")
    
    output_lines.append("\n" + "=" * 80)
    output_lines.append("2. Check if other users have Jan 5 data")
    output_lines.append("=" * 80)
    
    all_users = User.query.all()
    other_users_with_jan5_data = []
    
    for user in all_users:
        if user.email in target_emails:
            continue
        
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
        output_lines.append(f"\nWARNING: Found {len(other_users_with_jan5_data)} non-test users with Jan 5 data:")
        for item in other_users_with_jan5_data:
            user = item['user']
            count = item['count']
            output_lines.append(f"  - {user.name} ({user.email}): {count} records")
    else:
        output_lines.append("\nOK: No other users have Jan 5 data")
    
    output_lines.append("\n" + "=" * 80)
    output_lines.append("3. All unread alerts for target users")
    output_lines.append("=" * 80)
    
    for email in target_emails:
        user = User.query.filter_by(email=email).first()
        if not user:
            continue
        
        unread_alerts = ScoreAlert.query.filter_by(
            user_id=user.id,
            is_read=False
        ).order_by(ScoreAlert.alert_date.desc()).all()
        
        output_lines.append(f"\n{user.name}: {len(unread_alerts)} unread alerts")
        
        for alert in unread_alerts[:10]:
            try:
                lines = json.loads(alert.exceeded_lines)
                line_names = list(lines.keys())
                action = "Cross" if alert.alert_type == 'high' else "Approach"
                output_lines.append(f"  - {alert.alert_date} [{alert.alert_type}] {action}: {', '.join(line_names)}")
            except:
                output_lines.append(f"  - {alert.alert_date} [{alert.alert_type}]")

# Write to file
with open('alert_check_result.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output_lines))

print("Output written to alert_check_result.txt")
for line in output_lines:
    print(line)
