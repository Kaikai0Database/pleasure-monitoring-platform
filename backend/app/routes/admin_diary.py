from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, User, Diary
from sqlalchemy import desc

admin_diary_bp = Blueprint('admin_diary', __name__)


def verify_admin():
    """Helper function to verify admin token"""
    identity = get_jwt_identity()
    if not identity.startswith('admin_'):
        return None
    return int(identity.replace('admin_', ''))


@admin_diary_bp.route('/<int:patient_id>', methods=['GET'])
@jwt_required()
def get_patient_diaries(patient_id):
    """Get patient's diaries (read-only for admin)"""
    try:
        staff_id = verify_admin()
        if not staff_id:
            return jsonify({'success': False, 'message': '無效的管理員權限'}), 403
        
        # Verify patient exists
        patient = User.query.get(patient_id)
        if not patient:
            return jsonify({'success': False, 'message': '病人不存在'}), 404
        
        # Get patient's diaries
        diaries = Diary.query.filter_by(
            user_id=patient_id
        ).order_by(desc(Diary.date)).all()
        
        return jsonify({
            'success': True,
            'diaries': [diary.to_dict() for diary in diaries]
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'獲取日記失敗: {str(e)}'}), 500
