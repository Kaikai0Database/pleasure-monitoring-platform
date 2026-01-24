from app import create_app
from app.models import db, User, AssessmentHistory

app = create_app()

with app.app_context():
    clinical_users = User.query.filter_by(group='clinical').all()
    
    for u in clinical_users:
        print(f"User: {u.name} (ID: {u.id})")
        histories = AssessmentHistory.query.filter_by(user_id=u.id).all()
        for h in histories:
            print(f"  ID: {h.id}, Score: {h.total_score}, Level: '{h.level}', Max: {h.max_score}, Deleted: {h.is_deleted}")
