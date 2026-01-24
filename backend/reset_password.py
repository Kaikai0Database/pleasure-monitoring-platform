from app import create_app
from app.models import db, User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    user = User.query.filter_by(email='angel921030chenen@gmail.com').first()
    
    if user:
        new_password = '123456789'
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        
        print(f'[OK] Password reset successfully for user: {user.name}')
        print(f'   Email: {user.email}')
        print(f'   New password: {new_password}')
    else:
        print('[!] User not found')
