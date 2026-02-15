from app import create_app
from app.models import User

app = create_app()

with app.app_context():
    user = User.query.filter_by(email='angel921030chenen@gmail.com').first()
    if user:
        print(f"User: {user.name}")
        print(f"Email: {user.email}")
        print(f"Group: '{user.group}'")
    else:
        print("User not found")
