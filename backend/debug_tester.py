from app import create_app
from app.models import ScoreAlert, User, AssessmentHistory
from app.utils.alert_utils import calculate_moving_average, calculate_daily_average
from datetime import date
import json

app = create_app()

with app.app_context():
    # 檢查Tester
    user = User.query.filter_by(email='test_update@example.com').first()
    
    if not user:
        print("找不到Tester帳號")
    else:
        print(f"Tester帳號檢查 (ID: {user.id})")
        print("="*70)
        
        # 獲取所有警告
        all_alerts = ScoreAlert.query.filter_by(user_id=user.id).order_by(ScoreAlert.alert_date.desc()).all()
        
        print(f"\n所有警告（包括已讀）: {len(all_alerts)}")
        for alert in all_alerts:
            try:
                lines = json.loads(alert.exceeded_lines) if alert.exceeded_lines else {}
            except:
                lines = {}
            
            read_status = "已讀" if alert.is_read else "未讀"
            alert_type_cn = "高分" if alert.alert_type == 'high' else "低分"
            print(f"  日期:{alert.alert_date} [{alert_type_cn}] {read_status} - {list(lines.keys())}")
        
        # 檢查1/5的測驗
        jan5 = date(2026, 1, 5)
        jan5_assessments = AssessmentHistory.query.filter(
            AssessmentHistory.user_id == user.id,
            AssessmentHistory.completed_at >= jan5,
            AssessmentHistory.completed_at < date(2026, 1, 6)
        ).all()
        
        print(f"\n1/5測驗記錄: {len(jan5_assessments)}")
        for a in jan5_assessments:
            print(f"  {a.completed_at}: {a.total_score}/{a.max_score}")
        
        if jan5_assessments:
            # 計算1/5的移動平均和當日平均
            daily_avg, count = calculate_daily_average(user.id, jan5)
            ma_7 = calculate_moving_average(user.id, 7, jan5)
            ma_14 = calculate_moving_average(user.id, 14, jan5)
            ma_30 = calculate_moving_average(user.id, 30, jan5)
            
            print(f"\n1/5分析:")
            print(f"  當日平均: {daily_avg:.2f}")
            if ma_7: print(f"  7日線:  {ma_7:.2f}")
            if ma_14: print(f"  14日線: {ma_14:.2f}")
            if ma_30: print(f"  30日線: {ma_30:.2f}")
            
            # 檢查應該觸發什麼警告
            print(f"\n應該觸發:")
            if ma_7 and daily_avg > ma_7:
                print(f"  ✓ 高分警告 (超過7日線)")
            if ma_14 and daily_avg > ma_14:
                print(f"  ✓ 高分警告 (超過14日線)")
            if ma_30 and daily_avg > ma_30:
                print(f"  ✓ 高分警告 (超過30日線)")
            
            if ma_7 and 0 < (ma_7 - daily_avg) <= 3:
                print(f"  ✓ 低分警告 (接近7日線，差距{ma_7 - daily_avg:.2f})")
            if ma_14 and 0 < (ma_14 - daily_avg) <= 3:
                print(f"  ✓ 低分警告 (接近14日線，差距{ma_14 - daily_avg:.2f})")
            if ma_30 and 0 < (ma_30 - daily_avg) <= 3:
                print(f"  ✓ 低分警告 (接近30日線，差距{ma_30 - daily_avg:.2f})")
        
        # 檢查未讀警告
        unread_alerts = ScoreAlert.query.filter_by(
            user_id=user.id,
            is_read=False
        ).all()
        
        print(f"\n未讀警告數量: {len(unread_alerts)}")
        if len(unread_alerts) == 0:
            print("⚠️ 這就是為什麼沒有icon的原因！")
