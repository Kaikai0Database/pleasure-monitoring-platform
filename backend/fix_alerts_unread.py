"""
將 Tester 和唐洋雞的 1月5日警告標記為未讀
"""
from app import create_app, db
from app.models import User, ScoreAlert
from datetime import date

app = create_app()

with app.app_context():
    # 目標帳號
    target_emails = ['test_update@example.com', '111025048@live.asia.edu.tw']
    
    print("=== 將 1月5日警告標記為未讀 ===\n")
    
    for email in target_emails:
        user = User.query.filter_by(email=email).first()
        
        if not user:
            print(f"❌ 找不到用戶: {email}\n")
            continue
            
        print(f"👤 {user.name} ({email})")
        
        # 找出 1月5日的所有警告
        jan5_alerts = ScoreAlert.query.filter_by(
            user_id=user.id,
            alert_date=date(2026, 1, 5)
        ).all()
        
        if not jan5_alerts:
            print(f"   ⚠️  沒有 1月5日的警告")
            continue
        
        print(f"   找到 {len(jan5_alerts)} 個 1月5日警告")
        
        for alert in jan5_alerts:
            old_status = "已讀" if alert.is_read else "未讀"
            alert.is_read = False
            db.session.add(alert)
            print(f"   ✅ {alert.alert_type} 警告: {old_status} → 未讀")
        
        print()
    
    # 提交變更
    db.session.commit()
    print("\n✅ 所有變更已保存！")
    
    # 驗證
    print("\n=== 驗證結果 ===\n")
    for email in target_emails:
        user = User.query.filter_by(email=email).first()
        if user:
            unread_count = ScoreAlert.query.filter_by(
                user_id=user.id,
                is_read=False
            ).count()
            print(f"{user.name}: 未讀警告數 = {unread_count}")
