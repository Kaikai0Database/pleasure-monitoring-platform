from app import create_app
from app.models import ScoreAlert, User
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
    print("檢查5個目標帳號的警告狀態\n")
    print("="*70)
    
    total_users_with_dual = 0
    
    for email in target_emails:
        user = User.query.filter_by(email=email).first()
        if not user:
            continue
        
        # 獲取1/5的未讀警告
        alerts = ScoreAlert.query.filter_by(
            user_id=user.id,
            alert_date=jan5,
            is_read=False
        ).all()
        
        high_alerts = [a for a in alerts if a.alert_type == 'high']
        low_alerts = [a for a in alerts if a.alert_type == 'low']
        
        has_both = len(high_alerts) > 0 and len(low_alerts) > 0
        
        if has_both:
            total_users_with_dual += 1
            status = "✅ 雙警告"
        elif len(high_alerts) > 0:
            status = "🔔 僅高分"
        elif len(low_alerts) > 0:
            status = "📉 僅低分"
        else:
            status = "❌ 無警告"
        
        print(f"\n{user.name:15} ({email})")
        print(f"  狀態: {status}")
        
        for alert in alerts:
            try:
                lines = json.loads(alert.exceeded_lines)
            except:
                lines = {}
            
            alert_icon = "🔔" if alert.alert_type == 'high' else "📉"
            alert_text = "穿越" if alert.alert_type == 'high' else "接近"
            print(f"    {alert_icon} {alert_text}: {', '.join([f'{k}線' for k in lines.keys()])}")
    
    print("\n" + "="*70)
    print(f"\n總結：{total_users_with_dual}/5 個帳號同時擁有高分和低分警告")
    
    if total_users_with_dual == 5:
        print("✅ 成功！所有帳號都有雙警告")
    elif total_users_with_dual > 0:
        print("⚠️ 部分帳號成功，可能需要調整")
    else:
        print("❌ 未成功創建雙警告，需要重新調整策略")
