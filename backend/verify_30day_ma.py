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
    daily_data = []
    daily_scores = defaultdict(list)
    
    for a in assessments:
        date_key = a.completed_at.date()
        daily_scores[date_key].append(a.total_score)
    
    # 按日期排序並計算每日平均
    for date in sorted(daily_scores.keys()):
        scores = daily_scores[date]
        avg = sum(scores) / len(scores)
        daily_data.append({
            'date': date,
            'avg': avg,
            'scores': scores
        })
    
    print(f"Total days: {len(daily_data)}")
    print("\nCalculating 30-day moving average from day 30 onwards:\n")
    
    # 計算30日移動平均（從第30天開始）
    for i in range(29, min(35, len(daily_data))):  # 只看第30-35天
        # 取最近30天的數據
        window = daily_data[i-29:i+1]
        window_avgs = [d['avg'] for d in window]
        
        moving_avg = sum(window_avgs) / len(window_avgs)
        
        print(f"Day {i+1} ({daily_data[i]['date']}):")
        print(f"  Daily avg: {daily_data[i]['avg']:.2f}")
        print(f"  30-day MA (raw): {moving_avg:.10f}")
        print(f"  30-day MA (1 decimal): {round(moving_avg, 1)}")
        print(f"  Window size: {len(window_avgs)}")
        print()
    
    # 檢查最後幾天
    print("\nLast 6 days (including 1/3):")
    for i in range(-6, 0):
        idx = len(daily_data) + i
        if idx >= 29:  # 有30日移動平均
            window = daily_data[idx-29:idx+1]
            window_avgs = [d['avg'] for d in window]
            moving_avg = sum(window_avgs) / len(window_avgs)
            
            print(f"Day {idx+1} ({daily_data[idx]['date']}):")
            print(f"  Daily avg: {daily_data[idx]['avg']:.2f}")
            print(f"  30-day MA (raw): {moving_avg:.10f}")
            print(f"  30-day MA (1 decimal): {round(moving_avg, 1)}")
            print()
