from app import create_app
from app.models import db, User
from werkzeug.security import check_password_hash

app = create_app()

with app.app_context():
    user = User.query.filter_by(email='yfu202084@gmail.com').first()
    
    if user:
        print(f'✅ User found: {user.name}')
        print(f'📧 Email: {user.email}')
        
        # Test password
        passwords_to_test = ['Douglas930708', 'douglas930708', 'Douglas930708', '123456']
        
        for pwd in passwords_to_test:
            result = check_password_hash(user.password_hash, pwd)
            print(f'Password "{pwd}": {"✅ Correct" if result else "❌ Wrong"}')
    else:
        print('❌ User not found')
