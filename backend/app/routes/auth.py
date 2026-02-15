from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate input
        if not data or not data.get('email') or not data.get('password') or not data.get('name'):
            return jsonify({'success': False, 'message': '缺少必要欄位'}), 400
        
        email = data['email']
        name = data['name']
        password = data['password']
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'success': False, 'message': '此電子郵件已被註冊'}), 400
        
        # Create new user
        password_hash = generate_password_hash(password)
        new_user = User(email=email, name=name, password_hash=password_hash)
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '註冊成功',
            'user': new_user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'註冊失敗: {str(e)}'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        print(f"[DEBUG] Patient login attempt: {data.get('email')}")
        
        # Validate input
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'success': False, 'message': '缺少電子郵件或密碼'}), 400
        
        email = data['email']
        password = data['password']
        
        # Find user
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({'success': False, 'message': '電子郵件或密碼錯誤'}), 401
        
        # Update login stats
        try:
            from datetime import datetime
            today = datetime.now().date()
            if user.last_login_date != today:
                user.daily_login_count = 1
                user.last_login_date = today
            else:
                user.daily_login_count = (user.daily_login_count or 0) + 1
            db.session.commit()
        except Exception as e:
            print(f"Failed to update login stats: {e}")
            # Don't fail login if stats fail

        # Create JWT token - identity must be a string
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'success': True,
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'登入失敗: {str(e)}'}), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information"""
    try:
        current_user_id = int(get_jwt_identity())  # Convert string to int
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'success': False, 'message': '用戶不存在'}), 404
        
        return jsonify({
            'success': True,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'獲取用戶資訊失敗: {str(e)}'}), 500


@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    try:
        current_user_id = int(get_jwt_identity())  # Convert string to int
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'success': False, 'message': '用戶不存在'}), 404

        if user.is_profile_completed:
            return jsonify({'success': False, 'message': '個人資料已填寫完成，無法再次修改'}), 403
            
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '缺少資料'}), 400

        # Update fields
        from datetime import datetime
        
        if 'nickname' in data: user.nickname = data['nickname']
        if 'dob' in data: 
            try:
                user.dob = datetime.strptime(data['dob'], '%Y-%m-%d').date()
            except:
                pass # Or handle error
        if 'gender' in data: user.gender = data['gender']
        if 'height' in data:
            try:
                user.height = float(data['height']) if data['height'] not in [None, ''] else None
            except (ValueError, TypeError):
                user.height = None
        if 'weight' in data:
            try:
                user.weight = float(data['weight']) if data['weight'] not in [None, ''] else None
            except (ValueError, TypeError):
                user.weight = None
        if 'education' in data: user.education = data['education']
        if 'marital_status' in data: user.marital_status = data['marital_status']
        if 'marriage_other' in data: user.marriage_other = data.get('marriage_other')
        if 'has_children' in data: user.has_children = bool(data['has_children'])
        if 'children_count' in data: user.children_count = int(data['children_count']) if data['children_count'] is not None else None
        if 'economic_status' in data: user.economic_status = data['economic_status']
        if 'family_structure' in data: user.family_structure = data['family_structure']
        if 'family_other' in data: user.family_other = data.get('family_other')
        if 'has_job' in data: user.has_job = bool(data['has_job'])
        if 'salary_range' in data: user.salary_range = data.get('salary_range')
        if 'location_city' in data: user.location_city = data['location_city']
        if 'location_district' in data: user.location_district = data['location_district']
        if 'living_situation' in data: user.living_situation = data['living_situation']
        if 'cohabitant_count' in data: user.cohabitant_count = int(data['cohabitant_count']) if data['cohabitant_count'] is not None else None
        if 'religion' in data: user.religion = bool(data['religion'])
        if 'religion_other' in data: user.religion_other = data.get('religion_other')
        if 'group' in data: user.group = data['group']
        
        # Mark profile as completed
        user.is_profile_completed = True
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '個人資料更新成功',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        import traceback
        error_detail = traceback.format_exc()
        print(f"Profile update error: {str(e)}")
        print(f"Traceback: {error_detail}")
        return jsonify({'success': False, 'message': f'更新失敗: {str(e)}', 'error_detail': str(e)}), 500


@auth_bp.route('/consent', methods=['POST'])
@jwt_required()
def submit_consent():
    """Record user consent to terms of service"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'success': False, 'message': '用戶不存在'}), 404
        
        # Mark user as consented
        user.has_consented = True
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '同意條款成功',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'記錄同意狀態失敗: {str(e)}'}), 500
