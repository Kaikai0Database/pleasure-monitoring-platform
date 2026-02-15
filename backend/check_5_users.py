from app import create_app
from app.models import ScoreAlert, User
import json

app = create_app()

target_emails = [
    'test_manual@gmail.com',
    'angel921030chen@gmail.com',
    '111025015@live.asia.edu.tw',
    'test_update@example.com',
    '111025048@live.asia.edu.tw'
]

with app.app_context():
    print("TARGET USERS ALERT STATUS")
    print("="*70)
    
    for email in target_emails:
        user = User.query.filter_by(email=email).first()
        if not user:
            print(f"{email}: NOT FOUND")
            continue
        
        alerts = ScoreAlert.query.filter_by(user_id=user.id, is_read=False).all()
        
        if alerts:
            print(f"❌ {user.name:20} ({email}): {len(alerts)} unread alert(s)")
            for alert in alerts:
                try:
                    lines = json.loads(alert.exceeded_lines)
                except:
                    lines = {}
                print(f"     [{alert.alert_type}] {alert.alert_date}: {list(lines.keys())}")
        else:
            print(f"✓  {user.name:20} ({email}): No alerts")
    
    print("="*70)
