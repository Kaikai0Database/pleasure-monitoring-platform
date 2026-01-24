from app import create_app
from app.models import ScoreAlert, User
import json

app = create_app()

# 測試帳號（不需要檢查的）
test_emails = [
    'test_manual@gmail.com',
    'angel921030chen@gmail.com',
    '111025015@live.asia.edu.tw',
    'test_update@example.com',
    '111025048@live.asia.edu.tw'
]

with app.app_context():
    # 獲取所有用戶
    all_users = User.query.all()
    
    print("檢查非測試帳號的警告狀態\n")
    print("="*70)
    
    other_users_with_alerts = []
    
    for user in all_users:
        # 跳過測試帳號
        if user.email in test_emails:
            continue
        
        # 獲取所有未讀警告
        unread_alerts = ScoreAlert.query.filter_by(
            user_id=user.id,
            is_read=False
        ).all()
        
        if unread_alerts:
            other_users_with_alerts.append((user, unread_alerts))
            
            print(f"\n{user.name} ({user.email})")
            print(f"  未讀警告數量: {len(unread_alerts)}")
            
            for alert in unread_alerts:
                try:
                    lines = json.loads(alert.exceeded_lines) if alert.exceeded_lines else {}
                except:
                    lines = {}
                
                alert_icon = "🔔" if alert.alert_type == 'high' else "📉"
                alert_text = "穿越" if alert.alert_type == 'high' else "接近"
                line_names = ', '.join([f'{k}線' for k in lines.keys()])
                
                print(f"    日期:{alert.alert_date} [{alert.alert_type.upper()}] {alert_text}: {line_names}")
    
    print("\n" + "="*70)
    print(f"\n總結: {len(other_users_with_alerts)} 個非測試帳號有未讀警告")
    
    if len(other_users_with_alerts) == 0:
        print("\n⚠️ 問題發現：所有非測試帳號都沒有未讀警告！")
        print("可能原因：自動清除邏輯將所有舊警告都標記為已讀了")
