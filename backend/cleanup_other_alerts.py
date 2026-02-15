from app import create_app, db
from app.models import ScoreAlert, User
from datetime import date

app = create_app()

# 目標測試帳號
target_emails = [
    'test_manual@gmail.com',
    'angel921030chen@gmail.com',
    '111025015@live.asia.edu.tw',
    'test_update@example.com',
    '111025048@live.asia.edu.tw'
]

jan5 = date(2026, 1, 5)

with app.app_context():
    # 獲取目標帳號的ID
    target_user_ids = []
    for email in target_emails:
        user = User.query.filter_by(email=email).first()
        if user:
            target_user_ids.append(user.id)
    
    print(f"目標測試帳號數量: {len(target_user_ids)}")
    print(f"目標帳號ID: {target_user_ids}\n")
    
    # 找出所有1/5的警告
    all_jan5_alerts = ScoreAlert.query.filter_by(alert_date=jan5).all()
    
    print(f"1/5總警告數: {len(all_jan5_alerts)}")
    
    # 刪除非目標帳號的1/5警告
    deleted_count = 0
    for alert in all_jan5_alerts:
        if alert.user_id not in target_user_ids:
            user = User.query.get(alert.user_id)
            email = user.email if user else "未知"
            print(f"刪除: {email} 的1/5警告")
            db.session.delete(alert)
            deleted_count += 1
    
    db.session.commit()
    
    print(f"\n已刪除 {deleted_count} 個非目標帳號的1/5警告")
    
    # 檢查目標帳號的警告狀態
    print("\n目標帳號的1/5警告狀態：")
    print("="*70)
    
    for email in target_emails:
        user = User.query.filter_by(email=email).first()
        if not user:
            continue
        
        alerts = ScoreAlert.query.filter_by(
            user_id=user.id,
            alert_date=jan5,
            is_read=False
        ).all()
        
        high_count = sum(1 for a in alerts if a.alert_type == 'high')
        low_count = sum(1 for a in alerts if a.alert_type == 'low')
        
        status = ""
        if high_count > 0 and low_count > 0:
            status = "✅ 雙警告"
        elif high_count > 0:
            status = "🔔 僅高分"
        elif low_count > 0:
            status = "📉 僅低分"
        else:
            status = "❌ 無警告"
        
        print(f"{user.name:15} - {status} (高:{high_count}, 低:{low_count})")
