"""
為 experttest1 和 experttest2 手動生成警報
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.models import User
from app.utils.alert_utils import check_and_create_alert
from datetime import date, timedelta

app = create_app()

with app.app_context():
    # 查找兩個測試帳號
    users = User.query.filter(User.email.in_(['experttest1@example.com', 'experttest2@example.com'])).all()
    
    if not users:
        print("❌ 未找到測試帳號")
        sys.exit(1)
    
    print("="*80)
    print("為 Expert Test 帳號生成警報")
    print("="*80)
    
    # 從 2025-12-01 到 2026-02-01，每天檢查警報
    start_date = date(2025, 12, 1)
    end_date = date(2026, 2, 1)
    
    for user in users:
        print(f"\n{'='*60}")
        print(f"處理用戶: {user.name} ({user.email})")
        print(f"{'='*60}")
        
        current_date = start_date
        alerts_generated = 0
        
        while current_date <= end_date:
            # 調用警報檢查函數
            created_alerts = check_and_create_alert(user.id, current_date)
            
            if created_alerts:
                alerts_generated += len(created_alerts)
                for alert in created_alerts:
                    print(f"  [{current_date}] {alert.alert_type.upper()} 警報: 日平均 {alert.daily_average}")
            
            current_date += timedelta(days=1)
        
        # 提交所有變更
        db.session.commit()
        
        print(f"\n總共生成: {alerts_generated} 個警報")
    
    print(f"\n{'='*80}")
    print("✅ 警報生成完成！")
    print(f"{'='*80}")
    
    # 顯示最終統計
    from app.models import ScoreAlert
    
    print("\n最終警報統計:")
    for user in users:
        total_alerts = ScoreAlert.query.filter_by(user_id=user.id).count()
        unread_alerts = ScoreAlert.query.filter_by(user_id=user.id, is_read=False).count()
        high_alerts = ScoreAlert.query.filter_by(user_id=user.id, alert_type='high').count()
        low_alerts = ScoreAlert.query.filter_by(user_id=user.id, alert_type='low').count()
        
        print(f"\n{user.name}:")
        print(f"  總警報數: {total_alerts}")
        print(f"  未讀警報: {unread_alerts}")
        print(f"  HIGH 警報: {high_alerts}")
        print(f"  LOW 警報: {low_alerts}")
        
        # 顯示最近的警報
        recent_alerts = ScoreAlert.query.filter_by(user_id=user.id).order_by(ScoreAlert.alert_date.desc()).limit(5).all()
        if recent_alerts:
            print(f"\n  最近 5 個警報:")
            for alert in recent_alerts:
                read_status = "已讀" if alert.is_read else "未讀"
                print(f"    {alert.alert_date} - {alert.alert_type.upper()} - 日平均:{alert.daily_average} - {read_status}")
