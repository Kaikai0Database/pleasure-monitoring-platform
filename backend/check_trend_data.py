from app import create_app
from app.models import db, User, AssessmentHistory
from collections import defaultdict

app = create_app()

with app.app_context():
    user = User.query.filter_by(email='trend_test@example.com').first()
    
    if not user:
        print("User not found")
        exit()
    
    # 獲取所有評估記錄
    assessments = AssessmentHistory.query.filter_by(
        user_id=user.id,
        is_deleted=False
    ).order_by(AssessmentHistory.completed_at).all()
    
    # 按日期分組計算每日平均
    daily_avg = defaultdict(list)
    for a in assessments:
        date_key = a.completed_at.date()
        daily_avg[date_key].append(a.total_score)
    
    sorted_dates = sorted(daily_avg.keys())
    
    print(f"Total records: {len(assessments)}")
    print(f"Total days: {len(daily_avg)}")
    print("\nFirst 10 days:")
    for date in sorted_dates[:10]:
        scores = daily_avg[date]
        avg = sum(scores) / len(scores)
        print(f"  {date}: avg={avg:.2f}, scores={scores}")
    
    print("\nLast 10 days:")
    for date in sorted_dates[-10:]:
        scores = daily_avg[date]
        avg = sum(scores) / len(scores)
        print(f"  {date}: avg={avg:.2f}, scores={scores}")
    
    # 統計
    all_daily_avgs = [sum(scores)/len(scores) for scores in daily_avg.values()]
    print(f"\nDaily average statistics:")
    print(f"  Min: {min(all_daily_avgs):.2f}")
    print(f"  Max: {max(all_daily_avgs):.2f}")
    print(f"  Mean: {sum(all_daily_avgs)/len(all_daily_avgs):.2f}")
