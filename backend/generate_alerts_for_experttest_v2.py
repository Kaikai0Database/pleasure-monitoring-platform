"""
為experttest1_2和experttest2_2生成警報記錄
基於他們的評估數據計算移動平均線並創建警報
"""

from app import create_app
from app.models import db, User, AssessmentHistory, ScoreAlert
from datetime import datetime, timedelta, date
import json

def calculate_daily_average(user_id, target_date):
    """計算指定日期的日平均分數"""
    # 轉換為datetime範圍（台灣時間）
    start = datetime(target_date.year, target_date.month, target_date.day, 0, 0, 0)
    end = datetime(target_date.year, target_date.month, target_date.day, 23, 59, 59)
    
    # 轉換為UTC
    start_utc = start - timedelta(hours=8)
    end_utc = end - timedelta(hours=8)
    
    # 查詢當天的測驗
    assessments = AssessmentHistory.query.filter(
        AssessmentHistory.user_id == user_id,
        AssessmentHistory.completed_at >= start_utc,
        AssessmentHistory.completed_at <= end_utc,
        AssessmentHistory.is_deleted == False
    ).all()
    
    if not assessments:
        return None
    
    avg = sum(a.total_score for a in assessments) / len(assessments)
    return round(avg, 2)


def calculate_ma(user_id, target_date, days):
    """計算指定日期的N日移動平均線"""
    end_date = target_date
    start_date = target_date - timedelta(days=days-1)
    
    # 按日期分組計算日平均
    daily_averages = []
    current_date = start_date
    
    while current_date <= end_date:
        daily_avg = calculate_daily_average(user_id, current_date)
        if daily_avg is not None:
            daily_averages.append(daily_avg)
        current_date += timedelta(days=1)
    
    if not daily_averages:
        return None
    
    ma = sum(daily_averages) / len(daily_averages)
    return round(ma, 2)


def generate_alerts_for_user(user_id, email):
    """為用戶生成2026/2/1的警報記錄"""
    app = create_app()
    
    with app.app_context():
        target_date = date(2026, 2, 1)
        
        # 計算當日平均
        daily_avg = calculate_daily_average(user_id, target_date)
        
        if daily_avg is None:
            print(f"⚠️  {email}: 2026/2/1 無評估數據")
            return
        
        # 計算移動平均線
        ma7 = calculate_ma(user_id, target_date, 7)
        ma14 = calculate_ma(user_id, target_date, 14)
        ma30 = calculate_ma(user_id, target_date, 30)
        
        print(f"\n📊 {email} - 2026/2/1")
        print(f"  當日平均：{daily_avg:.2f}分")
        print(f"  7日MA：{ma7:.2f}分")
        print(f"  14日MA：{ma14:.2f}分")
        print(f"  30日MA：{ma30:.2f}分")
        
        # 判斷是否產生警報
        # 高分警報：超越任一MA線
        exceeded_lines = {}
        
        if daily_avg > ma7:
            exceeded_lines['7日'] = ma7
        if daily_avg > ma14:
            exceeded_lines['14日'] = ma14
        if daily_avg > ma30:
            exceeded_lines['30日'] = ma30
        
        # 低分警報：接近任一MA線（差距<3分）
        approaching_lines = {}
        
        if abs(daily_avg - ma7) < 3 and daily_avg <= ma7:
            approaching_lines['7日'] = ma7
        if abs(daily_avg - ma14) < 3 and daily_avg <= ma14:
            approaching_lines['14日'] = ma14
        if abs(daily_avg - ma30) < 3 and daily_avg <= ma30:
            approaching_lines['30日'] = ma30
        
        # 創建警報記錄
        alerts_created = 0
        
        # 高分警報（超越）
        if exceeded_lines:
            # 檢查是否已存在
            existing_high = ScoreAlert.query.filter_by(
                user_id=user_id,
                alert_date=target_date,
                alert_type='high'
            ).first()
            
            if existing_high:
                print(f"  ⚠️  高分警報已存在，更新...")
                existing_high.daily_average = daily_avg
                existing_high.exceeded_lines = json.dumps(exceeded_lines, ensure_ascii=False)
                existing_high.is_read = False
            else:
                high_alert = ScoreAlert(
                    user_id=user_id,
                    alert_date=target_date,
                    daily_average=daily_avg,
                    exceeded_lines=json.dumps(exceeded_lines, ensure_ascii=False),
                    alert_type='high',
                    is_read=False
                )
                db.session.add(high_alert)
                alerts_created += 1
            
            print(f"  ✅ 高分警報 - 超越: {', '.join(exceeded_lines.keys())}")
        
        # 低分警報（接近）
        if approaching_lines:
            # 檢查是否已存在
            existing_low = ScoreAlert.query.filter_by(
                user_id=user_id,
                alert_date=target_date,
                alert_type='low'
            ).first()
            
            if existing_low:
                print(f"  ⚠️  低分警報已存在，更新...")
                existing_low.daily_average = daily_avg
                existing_low.exceeded_lines = json.dumps(approaching_lines, ensure_ascii=False)
                existing_low.is_read = False
            else:
                low_alert = ScoreAlert(
                    user_id=user_id,
                    alert_date=target_date,
                    daily_average=daily_avg,
                    exceeded_lines=json.dumps(approaching_lines, ensure_ascii=False),
                    alert_type='low',
                    is_read=False
                )
                db.session.add(low_alert)
                alerts_created += 1
            
            print(f"  ✅ 低分警報 - 接近: {', '.join(approaching_lines.keys())}")
        
        db.session.commit()
        
        if alerts_created == 0 and not exceeded_lines and not approaching_lines:
            print(f"  ℹ️  未滿足警報條件")
        elif alerts_created > 0:
            print(f"  🎉 成功創建 {alerts_created} 個警報")


if __name__ == '__main__':
    print("=" * 60)
    print("為測試帳號生成警報記錄")
    print("=" * 60)
    
    # 為兩個測試帳號生成警報
    test_accounts = [
        (22, 'experttest1_2@example.com'),
        (23, 'experttest2_2@example.com')
    ]
    
    for user_id, email in test_accounts:
        generate_alerts_for_user(user_id, email)
    
    print("\n" + "=" * 60)
    print("✅ 警報生成完成！")
    print("=" * 60)
    print("\n請重新整理前端頁面查看警報")
