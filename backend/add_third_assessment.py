#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Add third assessment for test.patient@example.com
"""

from app import create_app, db
from app.models import User, AssessmentHistory
from datetime import datetime, date
import json

app = create_app()

def add_third_assessment():
    with app.app_context():
        # Find user
        user = User.query.filter_by(email='test.patient@example.com').first()
        
        if not user:
            print("ERROR: User not found!")
            return
        
        print(f"User: {user.email}")
        print(f"ID: {user.id}")
        
        # Check today's assessments
        today = date.today()
        existing = AssessmentHistory.query.filter(
            AssessmentHistory.user_id == user.id,
            db.func.date(AssessmentHistory.completed_at) == today
        ).all()
        
        print(f"\nToday assessments: {len(existing)}")
        for i, a in enumerate(existing):
            print(f"  {i+1}. {a.completed_at.strftime('%H:%M')} - {a.total_score}")
        
        if len(existing) >= 3:
            print("\nAlready have 3+ assessments today!")
            return
        
        # Add third assessment
        assessment = AssessmentHistory(
            user_id=user.id,
            total_score=48,
            max_score=100,
            level='Good',
            answers=json.dumps({
                'q1': 3, 'q2': 3, 'q3': 3, 'q4': 3, 'q5': 3,
                'q6': 3, 'q7': 3, 'q8': 3, 'q9': 3, 'q10': 3
            }),
            completed_at=datetime.now()
        )
        
        db.session.add(assessment)
        db.session.commit()
        
        print(f"\n[OK] Added 3rd assessment")
        print(f"  Score: {assessment.total_score}")
        print(f"  Time: {assessment.completed_at.strftime('%H:%M:%S')}")
        
        # Verify
        updated = AssessmentHistory.query.filter(
            AssessmentHistory.user_id == user.id,
            db.func.date(AssessmentHistory.completed_at) == today
        ).all()
        
        print(f"\nTotal today: {len(updated)}")
        
        # Calculate average
        scores = [a.total_score for a in updated]
        avg = sum(scores) / len(scores)
        print(f"Average: {avg:.1f}")

if __name__ == '__main__':
    add_third_assessment()
