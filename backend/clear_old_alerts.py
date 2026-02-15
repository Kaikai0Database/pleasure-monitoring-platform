from app import create_app, db
from app.models import ScoreAlert
from datetime import date

app = create_app()

jan5 = date(2026, 1, 5)

with app.app_context():
    print("清理所有非1/5的舊警告\n")
    print("="*70)
    
    # 獲取所有非1/5的警告
    old_alerts = ScoreAlert.query.filter(ScoreAlert.alert_date != jan5).all()
    
    print(f"找到 {len(old_alerts)} 個非1/5的警告，即將刪除...")
    
    deleted_by_date = {}
    for alert in old_alerts:
        date_str = str(alert.alert_date)
        if date_str not in deleted_by_date:
            deleted_by_date[date_str] = 0
        deleted_by_date[date_str] += 1
        db.session.delete(alert)
    
    db.session.commit()
    
    print("\n已刪除的警告（按日期分組）：")
    for date_str, count in sorted(deleted_by_date.items()):
        print(f"  {date_str}: {count} 個")
    
    print(f"\n總計刪除: {len(old_alerts)} 個舊警告")
    print("\n現在所有帳號只會顯示1/5的警告")
