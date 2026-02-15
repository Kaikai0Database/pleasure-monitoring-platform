from app import create_app, db
from app.models import User, AssessmentHistory, ScoreAlert
from app.utils.alert_utils import check_and_create_alert
from sqlalchemy import desc
from datetime import date

app = create_app()

# 測試帳號（需要排除的）
test_emails = [
    'test_manual@gmail.com',
    'angel921030chen@gmail.com',
    '111025015@live.asia.edu.tw',
    'test_update@example.com',
    '111025048@live.asia.edu.tw'
]

with app.app_context():
    print("為所有非測試帳號重新創建警告\n")
    print("="*70)
    
    # 獲取所有用戶
    all_users = User.query.all()
    
    recreated_count = 0
    
    for user in all_users:
        # 跳過測試帳號
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
        
        # 刪除該日期的舊警告（如果有）
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
            print(f"✓ {user.name:15} ({latest_date}): 創建了 {len(created_alerts)} 個警告")
            recreated_count += 1
            for alert in created_alerts:
                import json
                try:
                    lines = json.loads(alert.exceeded_lines)
                except:
                    lines = {}
                alert_type_cn = "高分" if alert.alert_type == 'high' else "低分"
                print(f"    [{alert_type_cn}] {list(lines.keys())}")
    
    print("\n" + "="*70)
    print(f"\n總結：為 {recreated_count} 個帳號重新創建了警告")
    print("\n請重新整理管理員頁面，現在應該可以看到所有帳號的警告圖標了")
