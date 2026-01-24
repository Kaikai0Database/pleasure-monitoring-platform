from app import create_app
from app.models import User, AssessmentHistory, ScoreAlert
from app.utils.alert_utils import calculate_moving_average, calculate_daily_average
from datetime import date
import json

app = create_app()

with app.app_context():
    # Check Test Manual
    user = User.query.filter_by(email='test_manual@gmail.com').first()
    if user:
        print(f"User: {user.name} ({user.email})")
        print(f"User ID: {user.id}")
        
        jan5 = date(2026, 1, 5)
        
        # Get Jan 5 assessments
        jan5_assessments = AssessmentHistory.query.filter(
            AssessmentHistory.user_id == user.id,
            AssessmentHistory.completed_at >= jan5,
            AssessmentHistory.completed_at < date(2026, 1, 6)
        ).all()
        
        print(f"\nJan 5 Assessments: {len(jan5_assessments)}")
        for a in jan5_assessments:
            print(f"  {a.completed_at}: Score {a.total_score}")
        
        # Calculate daily average
        daily_avg, count = calculate_daily_average(user.id, jan5)
        print(f"\nDaily Average on Jan 5: {daily_avg} (count: {count})")
        
        # Calculate MAs
        ma_7 = calculate_moving_average(user.id, 7, jan5)
        ma_14 = calculate_moving_average(user.id, 14, jan5)
        ma_30 = calculate_moving_average(user.id, 30, jan5)
        
        print(f"\nMoving Averages:")
        print(f"  7-day:  {ma_7}")
        print(f"  14-day: {ma_14}")
        print(f"  30-day: {ma_30}")
        
        if daily_avg:
            print(f"\nComparison:")
            if ma_7: print(f"  vs 7-day:  {daily_avg:.1f} {'>' if daily_avg > ma_7 else '<='} {ma_7:.1f}")
            if ma_14: print(f"  vs 14-day: {daily_avg:.1f} {'>' if daily_avg > ma_14 else '<='} {ma_14:.1f}")
            if ma_30: print(f"  vs 30-day: {daily_avg:.1f} {'>' if daily_avg > ma_30 else '<='} {ma_30:.1f}")
        
        # Check alerts
        alerts = ScoreAlert.query.filter_by(user_id=user.id, is_read=False).all()
        print(f"\nUnread Alerts: {len(alerts)}")
        for alert in alerts:
            try:
                lines = json.loads(alert.exceeded_lines)
            except:
                lines = {}
            print(f"  Date: {alert.alert_date}, Type: {alert.alert_type}, Lines: {list(lines.keys())}")
