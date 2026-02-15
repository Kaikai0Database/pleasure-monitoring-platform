"""
檢查 Tester 和唐洋雞帳號的警告狀態
"""
from app import create_app, db
from app.models import User, ScoreAlert
from datetime import date

app = create_app()

with app.app_context():
    # 先找出唐洋雞的正確 email
    tang_user = User.query.filter(User.name.like('%唐洋雞%')).first()
    
    if tang_user:
        print(f"找到唐洋雞帳號: {tang_user.email}\n")
        target_emails = ['test_update@example.com', tang_user.email]
    else:
        print("找不到唐洋雞帳號，只檢查 Tester\n")
        target_emails = ['test_update@example.com']
    
    print("=== 檢查警告狀態 ===\n")
    
    for email in target_emails:
        user = User.query.filter_by(email=email).first()
        
        if not user:
            print(f"❌ 找不到用戶: {email}\n")
            continue
            
        print(f"👤 {user.name} ({email})")
        print(f"   ID: {user.id}")
        
        # 查詢未讀警告
        unread_alerts = ScoreAlert.query.filter_by(
            user_id=user.id,
            is_read=False
        ).order_by(ScoreAlert.alert_date.desc()).all()
        
        print(f"   🔔 未讀警告數: {len(unread_alerts)}")
        
        if unread_alerts:
            for alert in unread_alerts:
                alert_type_icon = "🔔 高分" if alert.alert_type == 'high' else "📉 低分"
                print(f"      - {alert.alert_date} | {alert_type_icon} | 日均: {alert.daily_average}")
                print(f"        超越線: {alert.exceeded_lines}")
        
        # 查詢所有1月5日的警告
        jan5_all = ScoreAlert.query.filter_by(
            user_id=user.id,
            alert_date=date(2026, 1, 5)
        ).all()
        
        print(f"\n   📅 1月5日警告總數: {len(jan5_all)}")
        for alert in jan5_all:
            status = "已讀" if alert.is_read else "未讀"
            print(f"      - {alert.alert_type}: {status}, 線:{alert.exceeded_lines}")
        
        print("\n" + "="*70 + "\n")
