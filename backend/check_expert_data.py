"""
檢查 experttest1 和 experttest2 的數據和警報
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.models import User, AssessmentHistory
from datetime import datetime, date
from sqlalchemy import func

app = create_app()

with app.app_context():
    # 查找兩個測試帳號
    users = User.query.filter(User.email.in_(['experttest1@example.com', 'experttest2@example.com'])).all()
    
    if not users:
        print("❌ 未找到測試帳號")
        sys.exit(1)
    
    print("="*80)
    print("Expert Test 帳號數據檢查")
    print("="*80)
    
    for user in users:
        print(f"\n{'='*60}")
        print(f"用戶: {user.name} ({user.email})")
        print(f"ID: {user.id}")
        print(f"{'='*60}")
        
        # 查詢評估記錄總數
        total_assessments = AssessmentHistory.query.filter_by(user_id=user.id).count()
        print(f"總評估次數: {total_assessments}")
        
        # 查詢最後一天的評估（2026-02-01）
        last_day = date(2026, 2, 1)
        last_day_assessments = AssessmentHistory.query.filter(
            AssessmentHistory.user_id == user.id,
            func.date(AssessmentHistory.completed_at) == last_day
        ).all()
        
        if last_day_assessments:
            print(f"\n最後一天 (2026-02-01) 的評估:")
            print(f"  評估次數: {len(last_day_assessments)}")
            scores = [a.total_score for a in last_day_assessments]
            avg_score = sum(scores) / len(scores)
            print(f"  分數: {scores}")
            print(f"  日平均: {avg_score:.1f}")
        
        # 查詢最近幾天的評估
        print(f"\n最近7天的日平均分數:")
        for days_ago in range(6, -1, -1):
            check_date = date(2026, 2, 1) - __import__('datetime').timedelta(days=days_ago)
            day_assessments = AssessmentHistory.query.filter(
                AssessmentHistory.user_id == user.id,
                func.date(AssessmentHistory.completed_at) == check_date
            ).all()
            
            if day_assessments:
                scores = [a.total_score for a in day_assessments]
                avg = sum(scores) / len(scores)
                print(f"  {check_date}: {avg:.1f} 分 ({len(day_assessments)} 次評估)")
        
        # 檢查是否有警報表
        try:
            # 嘗試導入警報模型
            from app.models import Alert
            alerts = Alert.query.filter_by(user_id=user.id).order_by(Alert.created_at.desc()).limit(5).all()
            
            if alerts:
                print(f"\n最近的警報:")
                for alert in alerts:
                    print(f"  [{alert.alert_type}] {alert.alert_date}: {alert.alert_message}")
                    print(f"    已讀: {alert.is_read}")
            else:
                print(f"\n⚠️  未找到警報記錄")
        except:
            print(f"\n⚠️  警報表不存在或無法訪問")
    
    print(f"\n{'='*80}")
    print("✅ 數據檢查完成")
    print(f"{'='*80}")
    print("\n請登入管理後台查看圖表:")
    print("  URL: http://localhost:5174")
    print("  帳號: experttest1@example.com / test123")
    print("  帳號: experttest2@example.com / test123")
