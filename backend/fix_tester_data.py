from app import create_app, db
from app.models import User, AssessmentHistory
from app.utils.alert_utils import calculate_moving_average, check_and_create_alert
from datetime import datetime, date
import json

app = create_app()

with app.app_context():
    # 找到Tester
    user = User.query.filter_by(email='test_update@example.com').first()
    if not user:
        print("找不到Tester帳號")
        exit()
    
    print(f"重新創建Tester的雙警告資料")
    print("="*70)
    
    jan5 = date(2026, 1, 5)
    
    # 刪除現有的1/5測驗和警告
    existing_assessments = AssessmentHistory.query.filter(
        AssessmentHistory.user_id == user.id,
        db.func.date(AssessmentHistory.completed_at) == jan5
    ).all()
    
    if existing_assessments:
        print(f"刪除 {len(existing_assessments)} 筆現有1/5測驗...")
        for a in existing_assessments:
            db.session.delete(a)
        db.session.commit()
    
    # 計算移動平均
    ma_7 = calculate_moving_average(user.id, 7, jan5)
    ma_14 = calculate_moving_average(user.id, 14, jan5)
    ma_30 = calculate_moving_average(user.id, 30, jan5)
    
    print(f"\nTester的移動平均線：")
    print(f"  7日:  {ma_7:.2f}")
    print(f"  14日: {ma_14:.2f}")
    print(f"  30日: {ma_30:.2f}")
    
    # 目標：創建雙警告
    # 需要：超過某些線（如14日、30日）但接近7日線
    # 目標分數：39（超過14日38.52和30日38.19，接近7日41.52差距2.52）
    target_avg = ma_7 - 2.0  # 距離7日線2分（觸發LOW）
    
    print(f"\n目標當日平均: {target_avg:.2f}")
    
    # 確保也超過14日和30日線
    if target_avg <= ma_14 or target_avg <= ma_30:
        # 如果不夠高，調整到介於中間
        target_avg = (max(ma_14, ma_30) + min(ma_7, 100)) / 2
        print(f"調整後目標: {target_avg:.2f}")
    
    # 創建3個分數
    max_score = 56 if user.group == 'student' else 40
    scores = [
        int(target_avg + 0.5),
        int(target_avg - 0.5),
        int(target_avg)
    ]
    
    actual_avg = sum(scores) / 3
    print(f"\n創建分數: {scores}")
    print(f"實際平均: {actual_avg:.2f}")
    
    # 驗證
    print(f"\n驗證:")
    will_high = False
    will_low = False
    
    if actual_avg > ma_7:
        print(f"  ✓ 超過7日線 ({actual_avg:.2f} > {ma_7:.2f})")
        will_high = True
    if actual_avg > ma_14:
        print(f"  ✓ 超過14日線 ({actual_avg:.2f} > {ma_14:.2f})")
        will_high = True
    if actual_avg > ma_30:
        print(f"  ✓ 超過30日線 ({actual_avg:.2f} > {ma_30:.2f})")
        will_high = True
    
    diff_7 = ma_7 - actual_avg
    diff_14 = ma_14 - actual_avg
    diff_30 = ma_30 - actual_avg
    
    if 0 < diff_7 <= 3:
        print(f"  ✓ 接近7日線 (差距 {diff_7:.2f})")
        will_low = True
    if 0 < diff_14 <= 3:
        print(f"  ✓ 接近14日線 (差距 {diff_14:.2f})")
        will_low = True
    if 0 < diff_30 <= 3:
        print(f"  ✓ 接近30日線 (差距 {diff_30:.2f})")
        will_low = True
    
    if will_high and will_low:
        print("\n✅ 會觸發雙警告！")
    else:
        print(f"\n❌ 不會觸發雙警告（高:{will_high}, 低:{will_low}）")
    
    # 決定level
    if user.group == 'student':
        if actual_avg >= 42:
            level = '健康'
        elif actual_avg >= 28:
            level = '潛在憂鬱風險'
        else:
            level = '憂鬱'
    else:
        if actual_avg >= 30:
            level = '健康'
        elif actual_avg >= 20:
            level = '潛在憂鬱風險'
        else:
            level = '憂鬱'
    
    # 創建測驗
    times = [
        datetime(2026, 1, 5, 6, 0, 0),
        datetime(2026, 1, 5, 14, 0, 0),
        datetime(2026, 1, 5, 21, 0, 0)
    ]
    
    for score, timestamp in zip(scores, times):
        assessment = AssessmentHistory(
            user_id=user.id,
            total_score=score,
            max_score=max_score,
            level=level,
            completed_at=timestamp,
            is_deleted=False
        )
        db.session.add(assessment)
    
    db.session.commit()
    print("\n✓ 測驗已創建")
    
    # 觸發警告檢查
    print("\n執行警告檢查...")
    created_alerts = check_and_create_alert(user.id, jan5)
    
    if created_alerts:
        print(f"✓ 創建了 {len(created_alerts)} 個警告：")
        for alert in created_alerts:
            try:
                lines = json.loads(alert.exceeded_lines)
            except:
                lines = {}
            alert_name = "🔔 高分" if alert.alert_type == 'high' else "📉 低分"
            print(f"  {alert_name}: {list(lines.keys())}")
    else:
        print("❌ 未創建警告")
