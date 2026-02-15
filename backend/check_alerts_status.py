from app import create_app
from app.models import ScoreAlert, User

app = create_app()

with app.app_context():
    alerts = ScoreAlert.query.filter_by(is_read=False).all()
    print(f'Total unread alerts: {len(alerts)}')
    
    users_with_alerts = {}
    for a in alerts:
        if a.user_id not in users_with_alerts:
            users_with_alerts[a.user_id] = []
        users_with_alerts[a.user_id].append(a)
    
    print(f'Users with unread alerts: {len(users_with_alerts)}')
    
    for uid, alts in users_with_alerts.items():
        user = User.query.get(uid)
        if user:
            print(f"  - {user.email}: {len(alts)} alert(s)")
            for alert in alts:
                print(f"    Date: {alert.alert_date}, Type: {alert.alert_type}")
