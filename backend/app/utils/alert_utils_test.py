"""
測試模式的警報工具 - 放寬驗證條件
用於開發測試，單筆評估即可觸發警報
"""
from datetime import datetime, timedelta, date
from app.models import db, AssessmentHistory, ScoreAlert
import json


def calculate_moving_average_test(user_id, days, end_date=None):
    """
    測試模式：放寬 MA 計算條件
    只需要 1 天數據即可計算（原本需要 n/2 天）
    """
    if end_date is None:
        end_date = date.today()
    
    start_date = end_date - timedelta(days=days - 1)
    
    assessments = AssessmentHistory.query.filter(
        AssessmentHistory.user_id == user_id,
        AssessmentHistory.deleted_at.is_(None),
        db.func.date(AssessmentHistory.completed_at) >= start_date,
        db.func.date(AssessmentHistory.completed_at) <= end_date
    ).all()
    
    if not assessments:
        return None
    
    # 按日期分組計算日平均
    daily_scores = {}
    for assessment in assessments:
        assess_date = assessment.completed_at.date()
        if assess_date not in daily_scores:
            daily_scores[assess_date] = []
        daily_scores[assess_date].append(assessment.total_score)
    
    daily_averages = [sum(scores) / len(scores) for scores in daily_scores.values()]
    
    # 測試模式：只需要 1 天數據（原本需要 days/2）
    if len(daily_averages) < 1:
        return None
    
    return sum(daily_averages) / len(daily_averages)


def calculate_daily_average_test(user_id, target_date):
    """
    計算當日平均（不變）
    """
    assessments = AssessmentHistory.query.filter(
        AssessmentHistory.user_id == user_id,
        AssessmentHistory.deleted_at.is_(None),
        db.func.date(AssessmentHistory.completed_at) == target_date
    ).all()
    
    if not assessments:
        return None, 0
    
    total_score = sum(a.total_score for a in assessments)
    average = total_score / len(assessments)
    
    return average, len(assessments)


def check_and_create_alert_test(user_id, assessment_date):
    """
    測試模式的警報檢查
    
    放寬條件：
    1. 只需要 1 次評估（原本需要 3 次）
    2. MA 計算只需 1 天數據（原本需要 n/2 天）
    """
    print(f"\n[TEST MODE] 檢查警報 - User: {user_id}, Date: {assessment_date}")
    
    # 計算當日平均
    daily_avg, count = calculate_daily_average_test(user_id, assessment_date)
    
    if daily_avg is None:
        print("[TEST MODE] 無評估數據")
        return []
    
    print(f"[TEST MODE] 當日平均: {daily_avg:.1f}, 評估次數: {count}")
    
    # 測試模式：只需要 1 次評估（原本需要 3 次）
    if count < 1:
        print("[TEST MODE] 評估次數不足（需至少 1 次）")
        return []
    
    # 自動解除過去的未讀警報
    past_unread_alerts = ScoreAlert.query.filter(
        ScoreAlert.user_id == user_id,
        ScoreAlert.is_read == False,
        ScoreAlert.alert_date < assessment_date
    ).all()
    
    if past_unread_alerts:
        for alert in past_unread_alerts:
            alert.is_read = True
            db.session.add(alert)
        print(f"[TEST MODE] 標記 {len(past_unread_alerts)} 個過期警報為已讀")
    
    # 檢查今日是否已有警報
    existing_high_alert = ScoreAlert.query.filter_by(
        user_id=user_id,
        alert_date=assessment_date,
        alert_type='high'
    ).first()
    
    existing_low_alert = ScoreAlert.query.filter_by(
        user_id=user_id,
        alert_date=assessment_date,
        alert_type='low'
    ).first()
    
    # 使用測試模式的 MA 計算
    ma_7 = calculate_moving_average_test(user_id, 7, assessment_date)
    ma_14 = calculate_moving_average_test(user_id, 14, assessment_date)
    ma_30 = calculate_moving_average_test(user_id, 30, assessment_date)
    
    print(f"[TEST MODE] MA7: {ma_7}, MA14: {ma_14}, MA30: {ma_30}")
    
    created_alerts = []
    
    # 檢查 HIGH 穿線警報
    high_exceeded = {}
    
    if ma_7 is not None and daily_avg > ma_7:
        high_exceeded['7日'] = round(ma_7, 1)
        print(f"[TEST MODE] ✅ 穿越 7日線: {daily_avg:.1f} > {ma_7:.1f}")
    
    if ma_14 is not None and daily_avg > ma_14:
        high_exceeded['14日'] = round(ma_14, 1)
        print(f"[TEST MODE] ✅ 穿越 14日線: {daily_avg:.1f} > {ma_14:.1f}")
    
    if ma_30 is not None and daily_avg > ma_30:
        high_exceeded['30日'] = round(ma_30, 1)
        print(f"[TEST MODE] ✅ 穿越 30日線: {daily_avg:.1f} > {ma_30:.1f}")
    
    # 處理 HIGH 警報
    if high_exceeded:
        if existing_high_alert:
            existing_high_alert.daily_average = round(daily_avg, 1)
            existing_high_alert.exceeded_lines = json.dumps(high_exceeded, ensure_ascii=False)
            existing_high_alert.is_read = False
            db.session.add(existing_high_alert)
            print(f"[TEST MODE] 更新 HIGH 警報")
        else:
            alert = ScoreAlert(
                user_id=user_id,
                alert_date=assessment_date,
                daily_average=round(daily_avg, 1),
                exceeded_lines=json.dumps(high_exceeded, ensure_ascii=False),
                alert_type='high',
                is_read=False
            )
            db.session.add(alert)
            created_alerts.append(alert)
            print(f"[TEST MODE] 🔔 創建 HIGH 警報!")
    elif existing_high_alert:
        db.session.delete(existing_high_alert)
        print(f"[TEST MODE] 刪除不再符合的 HIGH 警報")
    
    # 檢查 LOW 接近線警報
    low_approached = {}
    
    if ma_7 is not None and 0 < (ma_7 - daily_avg) <= 3:
        low_approached['7日'] = round(ma_7, 1)
        print(f"[TEST MODE] ⚠️ 接近 7日線: 差距 {ma_7 - daily_avg:.1f} 分")
    
    if ma_14 is not None and 0 < (ma_14 - daily_avg) <= 3:
        low_approached['14日'] = round(ma_14, 1)
        print(f"[TEST MODE] ⚠️ 接近 14日線: 差距 {ma_14 - daily_avg:.1f} 分")
    
    if ma_30 is not None and 0 < (ma_30 - daily_avg) <= 3:
        low_approached['30日'] = round(ma_30, 1)
        print(f"[TEST MODE] ⚠️ 接近 30日線: 差距 {ma_30 - daily_avg:.1f} 分")
    
    # 處理 LOW 警報
    if low_approached:
        if existing_low_alert:
            existing_low_alert.daily_average = round(daily_avg, 1)
            existing_low_alert.exceeded_lines = json.dumps(low_approached, ensure_ascii=False)
            existing_low_alert.is_read = False
            db.session.add(existing_low_alert)
            print(f"[TEST MODE] 更新 LOW 警報")
        else:
            alert = ScoreAlert(
                user_id=user_id,
                alert_date=assessment_date,
                daily_average=round(daily_avg, 1),
                exceeded_lines=json.dumps(low_approached, ensure_ascii=False),
                alert_type='low',
                is_read=False
            )
            db.session.add(alert)
            created_alerts.append(alert)
            print(f"[TEST MODE] 📉 創建 LOW 警報!")
    elif existing_low_alert:
        db.session.delete(existing_low_alert)
        print(f"[TEST MODE] 刪除不再符合的 LOW 警報")
    
    db.session.commit()
    print(f"[TEST MODE] 完成! 創建了 {len(created_alerts)} 個新警報\n")
    
    return created_alerts
