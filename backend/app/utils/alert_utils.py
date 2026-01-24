"""
Alert utilities for score warnings
"""
from datetime import datetime, timedelta, date
from app.models import db, AssessmentHistory, ScoreAlert
import json


def calculate_moving_average(user_id, days, end_date=None):
    """
    Calculate moving average for the specified number of days
    
    Args:
        user_id: User ID
        days: Number of days for moving average (7, 14, or 30)
        end_date: End date for calculation (default: today)
    
    Returns:
        float or None: Moving average score or None if insufficient data
    """
    if end_date is None:
        end_date = date.today()
    
    # Calculate start date (include end_date, so subtract days-1)
    start_date = end_date - timedelta(days=days - 1)
    
    # Get all assessments in the date range
    assessments = AssessmentHistory.query.filter(
        AssessmentHistory.user_id == user_id,
        AssessmentHistory.deleted_at.is_(None),
        db.func.date(AssessmentHistory.completed_at) >= start_date,
        db.func.date(AssessmentHistory.completed_at) <= end_date
    ).all()
    
    if not assessments:
        return None
    
    # Group by date and calculate daily averages
    daily_scores = {}
    for assessment in assessments:
        assess_date = assessment.completed_at.date()
        if assess_date not in daily_scores:
            daily_scores[assess_date] = []
        daily_scores[assess_date].append(assessment.total_score)
    
    # Calculate average of daily averages
    daily_averages = [sum(scores) / len(scores) for scores in daily_scores.values()]
    
    # Need sufficient data (at least half the days)
    if len(daily_averages) < days / 2:
        return None
    
    return sum(daily_averages) / len(daily_averages)


def calculate_daily_average(user_id, target_date):
    """
    Calculate daily average score for a specific date
    
    Args:
        user_id: User ID
        target_date: Date to calculate
    
    Returns:
        tuple: (average_score, count) or (None, 0) if no data
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


def check_and_create_alert(user_id, assessment_date):
    """
    Check if daily average exceeds or approaches moving averages and create alerts if needed
    
    Alert types:
    - 'high': Daily average exceeds moving average (trend going up)
    - 'low': Daily average is within 3 points below moving average (early warning of downward trend)
    """
    # Calculate daily average
    daily_avg, count = calculate_daily_average(user_id, assessment_date)
    
    if daily_avg is None:
        return []
    
    # Only check after 3 assessments
    if count < 3:
        return []
    
    # 1. SPECIAL FEATURE: Auto-resolve past unread alerts
    # If a new assessment comes in (or average updates), we should mark past unread alerts as read
    # because the user's status has updated. This fulfills the requirement:
    # "If next daily average is lower... directly remove the bell" (by marking old one as read)
    past_unread_alerts = ScoreAlert.query.filter(
        ScoreAlert.user_id == user_id,
        ScoreAlert.is_read == False,
        ScoreAlert.alert_date < assessment_date
    ).all()
    
    if past_unread_alerts:
        for alert in past_unread_alerts:
            alert.is_read = True
            db.session.add(alert)
        # We'll commit these along with any new alerts
        
    # Check if alerts already exist for this date
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
    
    # Calculate moving averages
    ma_7 = calculate_moving_average(user_id, 7, assessment_date)
    ma_14 = calculate_moving_average(user_id, 14, assessment_date)
    ma_30 = calculate_moving_average(user_id, 30, assessment_date)
    
    created_alerts = []
    
    # Check HIGH score alerts (exceeds moving average)
    high_exceeded = {}
    
    if ma_7 is not None and daily_avg > ma_7:
        high_exceeded['7日'] = round(ma_7, 1)
    
    if ma_14 is not None and daily_avg > ma_14:
        high_exceeded['14日'] = round(ma_14, 1)
    
    if ma_30 is not None and daily_avg > ma_30:
        high_exceeded['30日'] = round(ma_30, 1)
    
    # Handle HIGH alert creation/update/resolution
    if high_exceeded:
        if existing_high_alert:
            # Update existing alert with latest average and lines
            existing_high_alert.daily_average = round(daily_avg, 1)
            existing_high_alert.exceeded_lines = json.dumps(high_exceeded, ensure_ascii=False)
            existing_high_alert.is_read = False  # Mark unread again if status persists/changes
            db.session.add(existing_high_alert)
        else:
            # Create new alert
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
    elif existing_high_alert:
        # If no longer high but existing alert exists for today, delete it
        # Requirement: "remove bell if lower than all lines" for today
        db.session.delete(existing_high_alert)

    # Check LOW score alerts (within 3 points below moving average)
    low_approached = {}
    
    # Check if daily average is below moving average but within 3 points
    # Triggers when: 0 < (ma - daily_avg) <= 3
    if ma_7 is not None and 0 < (ma_7 - daily_avg) <= 3:
        low_approached['7日'] = round(ma_7, 1)
    
    if ma_14 is not None and 0 < (ma_14 - daily_avg) <= 3:
        low_approached['14日'] = round(ma_14, 1)
    
    if ma_30 is not None and 0 < (ma_30 - daily_avg) <= 3:
        low_approached['30日'] = round(ma_30, 1)
    
    # Handle LOW alert creation/update/resolution
    if low_approached:
        if existing_low_alert:
            # Update existing alert
            existing_low_alert.daily_average = round(daily_avg, 1)
            existing_low_alert.exceeded_lines = json.dumps(low_approached, ensure_ascii=False)
            existing_low_alert.is_read = False
            db.session.add(existing_low_alert)
        else:
            # Create new alert
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
    elif existing_low_alert:
        # If no longer low but existing alert exists for today, remove it
        db.session.delete(existing_low_alert)

    # Commit all changes (updates, inserts, deletes)
    db.session.commit()
    
    # Return newly created alerts (if any)
    return created_alerts
