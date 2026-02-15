from app import create_app
from app.models import ScoreAlert, User, AssessmentHistory
from app.utils.alert_utils import calculate_moving_average, calculate_daily_average
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
    print("詳細檢查每個帳號\n")
    
    for email in target_emails:
        user = User.query.filter_by(email=email).first()
        if not user:
            continue
        
        print(f"\n{'='*70}")
        print(f"{user.name} ({email})")
        print("-"*70)
        
        # MA值
        ma_7 = calculate_moving_average(user.id, 7, jan5)
        ma_14 = calculate_moving_average(user.id, 14, jan5)
        ma_30 = calculate_moving_average(user.id, 30, jan5)
        
        # 當日平均
        daily_avg, count = calculate_daily_average(user.id, jan5)
        
        if ma_7: print(f"7日線:  {ma_7:.2f}")
        if ma_14: print(f"14日線: {ma_14:.2f}")
        if ma_30: print(f"30日線: {ma_30:.2f}")
        if daily_avg: print(f"當日:   {daily_avg:.2f}")
        
        # 警告
        alerts = ScoreAlert.query.filter_by(
            user_id=user.id,
            alert_date=jan5,
            is_read=False
        ).all()
        
        high_alerts = [a for a in alerts if a.alert_type == 'high']
        low_alerts = [a for a in alerts if a.alert_type == 'low']
        
        print(f"\n警告數量: 高={len(high_alerts)}, 低={len(low_alerts)}")
        
        for alert in alerts:
            try:
                lines = json.loads(alert.exceeded_lines)
            except:
                lines = {}
            
            alert_text = "穿越" if alert.alert_type == 'high' else "接近"
            print(f"  [{alert.alert_type.upper()}] {alert_text}: {', '.join([f'{k}線' for k in lines.keys()])}")
