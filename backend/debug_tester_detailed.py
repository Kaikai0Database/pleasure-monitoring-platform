"""
深入調查Tester帳號為何沒有警報
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import User, ScoreAlert, AssessmentHistory
from app.utils.alert_utils import calculate_daily_average, calculate_moving_average
from datetime import datetime, date
import json

app = create_app()

jan5 = date(2026, 1, 5)
jan6 = date(2026, 1, 6)

output_lines = []

with app.app_context():
    user = User.query.filter_by(email='test_update@example.com').first()
    
    if not user:
        output_lines.append("ERROR: Tester account not found!")
    else:
        output_lines.append(f"=== Tester Account Debug (ID: {user.id}) ===\n")
        
        # 1. Check Jan 5 assessments
        assessments = AssessmentHistory.query.filter(
            AssessmentHistory.user_id == user.id,
            AssessmentHistory.completed_at >= datetime.combine(jan5, datetime.min.time()),
            AssessmentHistory.completed_at < datetime.combine(jan6, datetime.min.time())
        ).all()
        
        output_lines.append(f"1. Jan 5 assessments: {len(assessments)}")
        for a in assessments:
            output_lines.append(f"   - {a.completed_at}: {a.total_score}/{a.max_score}")
        
        # 2. Calculate daily average and moving averages
        if assessments:
            daily_avg, count = calculate_daily_average(user.id, jan5)
            ma_7 = calculate_moving_average(user.id, 7, jan5)
            ma_14 = calculate_moving_average(user.id, 14, jan5)
            ma_30 = calculate_moving_average(user.id,  30, jan5)
            
            output_lines.append(f"\n2. Calculated values:")
            output_lines.append(f"   Daily Average: {daily_avg:.2f} (count={count})")
            output_lines.append(f"   7-day MA:  {f'{ma_7:.2f}' if ma_7 else 'None'}")
            output_lines.append(f"   14-day MA: {f'{ma_14:.2f}' if ma_14 else 'None'}")
            output_lines.append(f"   30-day MA: {f'{ma_30:.2f}' if ma_30 else 'None'}")
            
            # 3. Check what alerts SHOULD be triggered
            output_lines.append(f"\n3. Expected alert conditions:")
            
            high_lines = []
            low_lines = []
            
            if ma_7:
                if daily_avg > ma_7:
                    high_lines.append(f"7日 (avg {daily_avg:.2f} > ma {ma_7:.2f})")
                diff = ma_7 - daily_avg
                if 0 < diff <= 3:
                    low_lines.append(f"7日 (diff {diff:.2f})")
            
            if ma_14:
                if daily_avg > ma_14:
                    high_lines.append(f"14日 (avg {daily_avg:.2f} > ma {ma_14:.2f})")
                diff = ma_14 - daily_avg
                if 0 < diff <= 3:
                    low_lines.append(f"14日 (diff {diff:.2f})")
            
            if ma_30:
                if daily_avg > ma_30:
                    high_lines.append(f"30日 (avg {daily_avg:.2f} > ma {ma_30:.2f})")
                diff = ma_30 - daily_avg
                if 0 < diff <= 3:
                    low_lines.append(f"30日 (diff {diff:.2f})")
            
            if high_lines:
                output_lines.append(f"   HIGH alerts should trigger for: {', '.join(high_lines)}")
            else:
                output_lines.append(f"   HIGH alerts: NONE expected")
                
            if low_lines:
                output_lines.append(f"   LOW alerts should trigger for: {', '.join(low_lines)}")
            else:
                output_lines.append(f"   LOW alerts: NONE expected")
        
        # 4. Check actual alerts
        all_alerts = ScoreAlert.query.filter_by(
            user_id=user.id,
            alert_date=jan5
        ).all()
        
        output_lines.append(f"\n4. Actual alerts in database: {len(all_alerts)}")
        for alert in all_alerts:
            try:
                lines = json.loads(alert.exceeded_lines)
                line_names = list(lines.keys())
                status = "READ" if alert.is_read else "UNREAD"
                output_lines.append(f"   - [{alert.alert_type}] {status}: {', '.join(line_names)}")
            except:
                output_lines.append(f"   - [{alert.alert_type}] {alert.exceeded_lines}")
        
        # 5. Check if there's any data issue
        output_lines.append(f"\n5. Historical data check:")
        
        # Check how many days of historical data exists
        all_assessments = AssessmentHistory.query.filter(
            AssessmentHistory.user_id == user.id,
            AssessmentHistory.completed_at < datetime.combine(jan5, datetime.min.time())
        ).order_by(AssessmentHistory.completed_at.desc()).all()
        
        if all_assessments:
            # Group by date
            dates = {}
            for a in all_assessments:
                d = a.completed_at.date()
                if d not in dates:
                    dates[d] = []
                dates[d].append(a)
            
            output_lines.append(f"   Historical days before Jan 5: {len(dates)}")
            output_lines.append(f"   Latest 5 dates:")
            for d in sorted(dates.keys(), reverse=True)[:5]:
                scores = [f"{a.total_score}/{a.max_score}" for a in dates[d]]
                output_lines.append(f"     - {d}: {', '.join(scores)}")
        else:
            output_lines.append(f"   WARNING: No historical data before Jan 5!")

# Write to file
with open('tester_debug_result.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output_lines))

print("Output written to tester_debug_result.txt")
for line in output_lines:
    print(line)
