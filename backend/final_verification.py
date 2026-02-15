from app import create_app, db
from app.models import ScoreAlert, User
from datetime import date

app = create_app()

# 5個測試帳號
test_emails = [
    'test_manual@gmail.com',
    'angel921030chen@gmail.com',
    '111025015@live.asia.edu.tw',
    'test_update@example.com',
    '111025048@live.asia.edu.tw'
]

jan5 = date(2026, 1, 5)

with app.app_context():
    # 獲取測試帳號的ID
    test_user_ids = []
    for email in test_emails:
        user = User.query.filter_by(email=email).first()
        if user:
            test_user_ids.append(user.id)
    
    # 刪除所有非測試帳號的1/5警告
    print("清理非測試帳號的1/5警告...")
    all_jan5_alerts = ScoreAlert.query.filter_by(alert_date=jan5).all()
    
    deleted = 0
    for alert in all_jan5_alerts:
        if alert.user_id not in test_user_ids:
            db.session.delete(alert)
            deleted += 1
    
    db.session.commit()
    print(f"✓ 刪除了 {deleted} 個非測試帳號的1/5警告\n")
    
    # 驗證5個測試帳號
    print("5個測試帳號的1/5警告狀態：")
    print("="*70)
    
    for email in test_emails:
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
        
        if high_count > 0 and low_count > 0:
            status = "✅ 雙警告"
            import json
            for alert in alerts:
                try:
                    lines = json.loads(alert.exceeded_lines)
                except:
                    lines = {}
                alert_type_cn = "穿越" if alert.alert_type == 'high' else "接近"
                print(f"{user.name:15} - {status}")
                print(f"  [{alert.alert_type.upper()}] {alert_type_cn}: {', '.join([f'{k}線' for k in lines.keys()])}")
        elif high_count > 0:
            status = "🔔 僅高分"
            print(f"{user.name:15} - {status}")
        elif low_count > 0:
            status = "📉 僅低分"
            print(f"{user.name:15} - {status}")
        else:
            status = "❌ 無警告"
            print(f"{user.name:15} - {status}")
    
    # 檢查其他帳號是否還有1/5警告
    print("\n" + "="*70)
    other_jan5_alerts = ScoreAlert.query.filter(
        ScoreAlert.alert_date == jan5,
        ~ScoreAlert.user_id.in_(test_user_ids)
    ).all()
    
    if other_jan5_alerts:
        print(f"⚠️ 警告：還有 {len(other_jan5_alerts)} 個其他帳號的1/5警告")
    else:
        print("✅ 確認：只有測試帳號在1/5有警告")
