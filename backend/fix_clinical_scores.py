from app import create_app
from app.models import db, User, AssessmentHistory

app = create_app()

with app.app_context():
    # Find all clinical users
    clinical_users = User.query.filter_by(group='clinical').all()
    clinical_ids = [u.id for u in clinical_users]
    
    print(f"Found {len(clinical_users)} clinical users.")
    
    fixed_count = 0
    
    if clinical_ids:
        # Find incorrect histories for these users
        # Condition: Level is '需要關注' BUT score < 29
        bad_histories = AssessmentHistory.query.filter(
            AssessmentHistory.user_id.in_(clinical_ids),
            AssessmentHistory.level == '需要關注',
            AssessmentHistory.total_score < 29
        ).all()
        
        for h in bad_histories:
            print(f"Fixing Record {h.id}: User {h.user_id} Score {h.total_score} Level '{h.level}' -> '良好'")
            h.level = '良好'
            fixed_count += 1
            
        if fixed_count > 0:
            db.session.commit()
            print(f"Successfully fixed {fixed_count} records.")
        else:
            print("No incorrect records found.")
    else:
        print("No clinical users found.")
