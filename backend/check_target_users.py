from app import create_app
from app.models import ScoreAlert, User, AssessmentHistory
from datetime import date
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

with app.app_context():
    print("="*70)
    print("CHECKING TARGET USERS STATUS")
    print("="*70)
    
    for email in target_emails:
        user = User.query.filter_by(email=email).first()
        if not user:
            print(f"\n{email}: USER NOT FOUND")
            continue
        
        print(f"\n{user.name} ({email})")
        print("-" * 70)
        
        # Check Jan 5 assessments
        jan5_assessments = AssessmentHistory.query.filter(
            AssessmentHistory.user_id == user.id,
            AssessmentHistory.completed_at >= date(2026, 1, 5),
            AssessmentHistory.completed_at < date(2026, 1, 6)
        ).order_by(AssessmentHistory.completed_at).all()
        
        print(f"Jan 5 Assessments: {len(jan5_assessments)}")
        if jan5_assessments:
            scores = [a.total_score for a in jan5_assessments]
            avg = sum(scores) / len(scores)
            print(f"  Scores: {scores}")
            print(f"  Daily Average: {avg:.1f}")
            for a in jan5_assessments:
                print(f"    {a.completed_at.strftime('%H:%M')}: Score {a.total_score}")
        
        # Check unread alerts
        unread_alerts = ScoreAlert.query.filter_by(
            user_id=user.id,
            is_read=False
        ).all()
        
        print(f"\nUnread Alerts: {len(unread_alerts)}")
        if unread_alerts:
            for alert in unread_alerts:
                try:
                    lines = json.loads(alert.exceeded_lines) if alert.exceeded_lines else {}
                except:
                    lines = {}
                print(f"  [{alert.alert_type.upper()}] Date: {alert.alert_date}, Lines: {list(lines.keys())}, Avg: {alert.daily_average}")
        else:
            print("  ✓ No unread alerts")
    
    print("\n" + "="*70)
