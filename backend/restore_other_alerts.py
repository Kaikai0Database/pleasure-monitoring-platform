from app import create_app, db
from app.models import User, AssessmentHistory, ScoreAlert
from app.utils.alert_utils import check_and_create_alert
from sqlalchemy import desc

app = create_app()

# 5個測試帳號（只在1/5有測驗）
test_emails = [
    'test_manual@gmail.com',
    'angel921030chen@gmail.com',
    '111025015@live.asia.edu.tw',
    'test_update@example.com',
    '111025048@live.asia.edu.tw'
]

with app.app_context():
    print("為所有非測試帳號恢復警告\n")
    print("="*70)
    
    # 獲取所有用戶
    all_users = User.query.all()
    
    restored_count = 0
    
    for user in all_users:
        # 跳過測試帳號（他們已經有1/5的警告了）
        if user.email in test_emails:
            continue
        
        # 獲取該用戶最新的測驗
        latest_assessment = AssessmentHistory.query.filter_by(
            user_id=user.id,
            is_deleted=False
        ).order_by(desc(AssessmentHistory.completed_at)).first()
        
        if not latest_assessment:
            continue
        
        latest_date = latest_assessment.completed_at.date()
        
        # 檢查該日期是否已經有未讀警告
        existing_alerts = ScoreAlert.query.filter_by(
            user_id=user.id,
            alert_date=latest_date,
            is_read=False
        ).all()
        
        if existing_alerts:
            continue  # 已經有警告了，不需要重新創建
        
        # 刪除該日期的舊警告（如果有已讀的）
        old_alerts = ScoreAlert.query.filter_by(
            user_id=user.id,
            alert_date=latest_date
        ).all()
        
        for alert in old_alerts:
            db.session.delete(alert)
        
        db.session.commit()
        
        # 重新檢查並創建警告
        created_alerts = check_and_create_alert(user.id, latest_date)
        
        if created_alerts:
            print(f"✓ {user.name:20} ({latest_date}): 恢復了 {len(created_alerts)} 個警告")
            restored_count += 1
            
            import json
            for alert in created_alerts:
                try:
                    lines = json.loads(alert.exceeded_lines)
                except:
                    lines = {}
                alert_type_cn = "高分" if alert.alert_type == 'high' else "低分"
                action = "穿越" if alert.alert_type == 'high' else "接近"
                print(f"    [{alert_type_cn}] {action}: {', '.join([f'{k}線' for k in lines.keys()])}")
    
    print("\n" + "="*70)
    print(f"\n總結：為 {restored_count} 個非測試帳號恢復了警告")
    
    # 最終統計
    all_unread = ScoreAlert.query.filter_by(is_read=False).all()
    users_with_alerts = set([a.user_id for a in all_unread])
    
    print(f"\n當前狀態：")
    print(f"  總未讀警告數: {len(all_unread)}")
    print(f"  有警告的用戶數: {len(users_with_alerts)}")
    print(f"\n包含:")
    print(f"  - 5個測試帳號（1/5的雙警告）")
    print(f"  - {restored_count}個其他帳號（基於各自最新測驗日期）")
