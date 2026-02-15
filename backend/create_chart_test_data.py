"""
Create test patient data with comprehensive assessment history for chart testing
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.models import User, AssessmentHistory
from datetime import datetime, timedelta
import random

app = create_app()

with app.app_context():
    # Check if test patient already exists
    test_patient = User.query.filter_by(email='test.patient@example.com').first()
    
    if not test_patient:
        # Create test patient
        from werkzeug.security import generate_password_hash
        test_patient = User(
            email='test.patient@example.com',
            name='測試患者',
            nickname='Chart Test User',
            password_hash=generate_password_hash('test123'),
            group='clinical',
            created_at=datetime.now() - timedelta(days=60)
        )
        db.session.add(test_patient)
        db.session.commit()
        print(f"[OK] Created test patient: {test_patient.name} (ID: {test_patient.id})")
    else:
        print(f"[OK] Test patient already exists: {test_patient.name} (ID: {test_patient.id})")
    
    # Delete old assessment history for this patient
    old_assessments = AssessmentHistory.query.filter_by(user_id=test_patient.id).all()
    for assessment in old_assessments:
        db.session.delete(assessment)
    db.session.commit()
    print(f"[DELETE] Deleted {len(old_assessments)} old assessment records")
    
    # Create 45 days of assessment history (to show all charts properly)
    print("[INFO] Creating 45 days of assessment history...")
    
    base_score = 25  # Starting score
    assessments_created = 0
    
    for days_ago in range(44, -1, -1):  # 45 days total
        assessment_date = datetime.now() - timedelta(days=days_ago)
        
        # Add some variation to scores (simulate realistic patient data)
        # Trend: slight improvement over time with fluctuations
        trend_improvement = (44 - days_ago) * 0.3  # Gradual improvement
        daily_variation = random.randint(-3, 3)  # Daily fluctuation
        
        total_score = int(base_score + trend_improvement + daily_variation)
        total_score = max(5, min(total_score, 50))  # Clamp between 5-50
        
        # Determine level
        if total_score <= 12:
            level = '良好'
        elif total_score <= 24:
            level = '良好'
        else:
            level = '需要關注'
        
        # Create assessment with sample answers
        assessment = AssessmentHistory(
            user_id=test_patient.id,
            total_score=total_score,
            max_score=56,
            level=level,
            answers=str([{"questionId": i, "emoji": "emoji", "score": random.randint(0, 4)} for i in range(1, 15)]),
            completed_at=assessment_date
        )
        db.session.add(assessment)
        assessments_created += 1
    
    db.session.commit()
    print(f"[OK] Created {assessments_created} assessment records")
    
    # Print summary
    print("\n" + "="*60)
    print("TEST DATA SUMMARY")
    print("="*60)
    print(f"Patient: {test_patient.name} ({test_patient.email})")
    print(f"Patient ID: {test_patient.id}")
    print(f"Total Assessments: {assessments_created}")
    print(f"Date Range: {(datetime.now() - timedelta(days=44)).strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}")
    print(f"Score Range: ~{base_score} to ~{base_score + 44*0.3}")
    print("\n[OK] All charts should now display data:")
    print("  - Comprehensive trend (1/7/14/30 day)")
    print("  - Daily average (last 30 days)")
    print("  - 7-day trend")
    print("  - 14-day trend")
    print("  - 30-day trend")
    print("="*60)
    print(f"\n[LINK] Admin can view at: http://localhost:5174")
    print(f"[LINK] Patient Detail (ID: {test_patient.id})")
    print("="*60)
