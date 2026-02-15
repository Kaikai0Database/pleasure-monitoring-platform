from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.admin_models import db, HealthcareStaff

admin_auth_bp = Blueprint('admin_auth', __name__)

@admin_auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new healthcare staff member"""
    try:
        data = request.get_json()
        
        # Validate input
        if not data or not data.get('email') or not data.get('password') or not data.get('name'):
            return jsonify({'success': False, 'message': '缺少必要欄位'}), 400
        
        email = data['email']
        name = data['name']
        password = data['password']
        role = data.get('role', '醫護人員')
        
        # Check if staff already exists
        existing_staff = HealthcareStaff.query.filter_by(email=email).first()
        if existing_staff:
            return jsonify({'success': False, 'message': '此電子郵件已被註冊'}), 400
        
        # Create new staff
        password_hash = generate_password_hash(password)
        new_staff = HealthcareStaff(
            email=email, 
            name=name, 
            password_hash=password_hash,
            role=role
        )
        
        db.session.add(new_staff)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '註冊成功',
            'staff': new_staff.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'註冊失敗: {str(e)}'}), 500


@admin_auth_bp.route('/login', methods=['POST'])
def login():
    """Login healthcare staff"""
    try:
        data = request.get_json()
        print(f"[DEBUG] Admin login attempt: {data.get('email')}")
        
        # Validate input
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'success': False, 'message': '缺少電子郵件或密碼'}), 400
        
        email = data['email']
        password = data['password']
        
        # Find staff
        staff = HealthcareStaff.query.filter_by(email=email).first()
        if not staff or not check_password_hash(staff.password_hash, password):
            return jsonify({'success': False, 'message': '電子郵件或密碼錯誤'}), 401
        
        # Create JWT token with 'admin_' prefix to distinguish from patient tokens
        access_token = create_access_token(identity=f'admin_{staff.id}')
        
        return jsonify({
            'success': True,
            'access_token': access_token,
            'staff': staff.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'登入失敗: {str(e)}'}), 500


@admin_auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_staff():
    """Get current staff information"""
    try:
        identity = get_jwt_identity()
        
        # Verify this is an admin token
        if not identity.startswith('admin_'):
            return jsonify({'success': False, 'message': '無效的管理員權限'}), 403
        
        # Extract staff ID
        staff_id = int(identity.replace('admin_', ''))
        staff = HealthcareStaff.query.get(staff_id)
        
        if not staff:
            return jsonify({'success': False, 'message': '管理員不存在'}), 404
        
        return jsonify({
            'success': True,
            'staff': staff.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'獲取管理員資訊失敗: {str(e)}'}), 500
