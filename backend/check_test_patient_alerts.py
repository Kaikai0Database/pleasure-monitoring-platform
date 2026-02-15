"""
Check test patient alerts and assessment data
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.models import User, AssessmentHistory, ScoreAlert
from datetime import datetime, date
import json

app = create_app()

with app.app_context():
    # Find test patient
    test_patient = User.query.filter_by(email='test.patient@example.com').first()
    
    if not test_patient:
        print("❌ Test patient not found!")
        sys.exit(1)
    
    print(f"✅ Found patient: {test_patient.name} (ID: {test_patient.id})")
    print(f"   Email: {test_patient.email}")
    print(f"   Group: {test_patient.group}")
    print()
    
    # Check today's assessments
    today = date.today()
    today_assessments = AssessmentHistory.query.filter(
        AssessmentHistory.user_id == test_patient.id,
        AssessmentHistory.deleted_at.is_(None),
        db.func.date(AssessmentHistory.completed_at) == today
    ).all()
    
    print(f"📅 Today's Date: {today}")
    print(f"📊 Today's Assessments: {len(today_assessments)}")
    
    if today_assessments:
        scores = [a.total_score for a in today_assessments]
        avg_score = sum(scores) / len(scores)
        print(f"   Scores: {scores}")
        print(f"   Daily Average: {avg_score:.1f}")
    else:
        print("   ⚠️  No assessments today - this is why no alerts show!")
    print()
    
    # Check recent assessments (last 10 days)
    recent_assessments = AssessmentHistory.query.filter(
        AssessmentHistory.user_id == test_patient.id,
        AssessmentHistory.deleted_at.is_(None)
    ).order_by(AssessmentHistory.completed_at.desc()).limit(50).all()
    
    print(f"📈 Recent Assessment History (last 50):")
    from collections import defaultdict
    daily_data = defaultdict(list)
    
    for a in recent_assessments:
        date_key = a.completed_at.date()
        daily_data[date_key].append(a.total_score)
    
    for date_key in sorted(daily_data.keys(), reverse=True)[:10]:
        scores = daily_data[date_key]
        avg = sum(scores) / len(scores)
        print(f"   {date_key}: {len(scores)} assessments, avg={avg:.1f}, scores={scores}")
    print()
    
    # Check alerts in database
    alerts = ScoreAlert.query.filter_by(user_id=test_patient.id).order_by(ScoreAlert.alert_date.desc()).all()
    
    print(f"🔔 Alerts in Database: {len(alerts)}")
    for alert in alerts[:5]:  # Show last 5
        exceeded = json.loads(alert.exceeded_lines) if alert.exceeded_lines else {}
        status = "❌ Read" if alert.is_read else "✅ Unread"
        print(f"   {alert.alert_date} | {alert.alert_type.upper()} | {status}")
        print(f"      Daily Avg: {alert.daily_average} | Lines: {list(exceeded.keys())}")
    
    if not alerts:
        print("   ⚠️  No alerts in database!")
    print()
    
    # Check unread alerts specifically
    unread_alerts = ScoreAlert.query.filter_by(
        user_id=test_patient.id,
        is_read=False
    ).all()
    
    print(f"📬 Unread Alerts: {len(unread_alerts)}")
    for alert in unread_alerts:
        exceeded = json.loads(alert.exceeded_lines) if alert.exceeded_lines else {}
        print(f"   {alert.alert_date} | {alert.alert_type.upper()}")
        print(f"      Lines: {list(exceeded.keys())}")
    print()
    
    print("="*60)
    print("DIAGNOSIS:")
    print("="*60)
    
    if len(today_assessments) < 3:
        print("❌ PROBLEM: Not enough assessments today")
        print(f"   - Today: {len(today_assessments)} assessments")
        print("   - Required: >= 3 assessments")
        print()
        print("💡 SOLUTION: Patient needs to complete 3+ assessments today")
        print("   to trigger alert detection on frontend")
    elif len(unread_alerts) == 0:
        print("❌ PROBLEM: No unread alerts in database")
        print()
        print("💡 SOLUTION: Complete a new assessment to trigger alert")
        print("   calculation in backend")
    else:
        print("✅ Alerts exist but might not match frontend calculation")
        print("   Frontend uses real-time calculation based on today's data")
        print("   Backend uses stored alerts from database")
