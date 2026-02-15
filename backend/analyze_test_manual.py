from app import create_app
from app.models import User, AssessmentHistory
from app.utils.alert_utils import calculate_moving_average, calculate_daily_average
from datetime import date

app = create_app()

with app.app_context():
    user = User.query.filter_by(email='test_manual@gmail.com').first()
    jan5 = date(2026, 1, 5)
    
    # Calculate MA values on Jan 5
    ma_7 = calculate_moving_average(user.id, 7, jan5)
    ma_14 = calculate_moving_average(user.id, 14, jan5)
    ma_30 = calculate_moving_average(user.id, 30, jan5)
    
    # Get actual daily average
    daily_avg, count = calculate_daily_average(user.id, jan5)
    
    print("Test Manual - Jan 5 Analysis")
    print("="*60)
    print(f"Moving Averages:")
    print(f"  7-day:  {ma_7:.2f}" if ma_7 else "  7-day:  None")
    print(f"  14-day: {ma_14:.2f}" if ma_14 else "  14-day: None")
    print(f"  30-day: {ma_30:.2f}" if ma_30 else "  30-day: None")
    
    print(f"\nDaily Average on Jan 5: {daily_avg:.2f}")
    
    ma_values = [ma for ma in [ma_7, ma_14, ma_30] if ma is not None]
    print(f"\nRange of MA values: {min(ma_values):.2f} - {max(ma_values):.2f}")
    
    print(f"\nDaily avg {daily_avg:.2f} is:")
    if ma_7 and daily_avg > ma_7: print(f"  ABOVE 7-day MA ({ma_7:.2f})")
    if ma_14 and daily_avg > ma_14: print(f"  ABOVE 14-day MA ({ma_14:.2f})")
    if ma_30 and daily_avg > ma_30: print(f"  ABOVE 30-day MA ({ma_30:.2f})")
    
    # Get Jan 5 assessments
    jan5_assessments = AssessmentHistory.query.filter(
        AssessmentHistory.user_id == user.id,
        AssessmentHistory.completed_at >= jan5,
        AssessmentHistory.completed_at < date(2026, 1, 6)
    ).all()
    
    print(f"\nJan 5 Assessments ({len(jan5_assessments)} total):")
    for a in jan5_assessments:
        print(f"  {a.completed_at.strftime('%H:%M')}: {a.total_score}")
