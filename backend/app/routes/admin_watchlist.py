from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, User, AssessmentHistory
from app.admin_models import PatientWatchlist
from sqlalchemy import desc, func

admin_watchlist_bp = Blueprint('admin_watchlist', __name__)


def verify_admin():
    """Helper function to verify admin token"""
    identity = get_jwt_identity()
    if not identity.startswith('admin_'):
        return None
    return int(identity.replace('admin_', ''))


@admin_watchlist_bp.route('', methods=['GET'])
@jwt_required()
def get_watchlist():
    """Get staff's watchlist with patient details"""
    try:
        staff_id = verify_admin()
        if not staff_id:
            return jsonify({'success': False, 'message': '無效的管理員權限'}), 403
        
        # Get watchlist items for this staff, ordered by display_order (desc = higher values first)
        watchlist_items = PatientWatchlist.query.filter_by(
            staff_id=staff_id
        ).order_by(desc(PatientWatchlist.display_order)).all()
        
        result = []
        from datetime import datetime
        today = datetime.now().date()
        
        for item in watchlist_items:
            # Get patient details
            patient = User.query.get(item.patient_id)
            if not patient:
                continue
            
            # Get latest assessment
            latest_assessment = AssessmentHistory.query.filter_by(
                user_id=patient.id,
                is_deleted=False
            ).order_by(desc(AssessmentHistory.completed_at)).first()
            
            # Get average score
            avg_score = db.session.query(
                func.avg(AssessmentHistory.total_score)
            ).filter_by(
                user_id=patient.id,
                is_deleted=False
            ).scalar()
            
            watchlist_data = item.to_dict()
            patient_data = patient.to_dict()
            
            # Check if patient has been inactive for 5+ days
            inactive_warning = False
            if patient.last_login_date:
                days_since_login = (today - patient.last_login_date).days
                if days_since_login >= 5:
                    inactive_warning = True
            else:
                # If never logged in, also mark as inactive
                inactive_warning = True
            
            patient_data['inactive_warning'] = inactive_warning
            watchlist_data['patient'] = patient_data
            watchlist_data['latest_assessment'] = latest_assessment.to_dict() if latest_assessment else None
            watchlist_data['average_score'] = round(float(avg_score), 2) if avg_score else None
            
            result.append(watchlist_data)
        
        return jsonify({
            'success': True,
            'watchlist': result
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'獲取特別關注列表失敗: {str(e)}'}), 500


@admin_watchlist_bp.route('', methods=['POST'])
@jwt_required()
def add_to_watchlist():
    """Add a patient to watchlist"""
    try:
        staff_id = verify_admin()
        if not staff_id:
            return jsonify({'success': False, 'message': '無效的管理員權限'}), 403
        
        data = request.get_json()
        if not data or not data.get('patient_id'):
            return jsonify({'success': False, 'message': '缺少病人ID'}), 400
        
        patient_id = data['patient_id']
        notes = data.get('notes', '')
        
        # Verify patient exists
        patient = User.query.get(patient_id)
        if not patient:
            return jsonify({'success': False, 'message': '病人不存在'}), 404
        
        # Check if already in watchlist
        existing = PatientWatchlist.query.filter_by(
            staff_id=staff_id,
            patient_id=patient_id
        ).first()
        
        if existing:
            return jsonify({'success': False, 'message': '此病人已在特別關注列表中'}), 400
        
        # Get max display_order for this staff
        max_order = db.session.query(
            func.max(PatientWatchlist.display_order)
        ).filter_by(staff_id=staff_id).scalar() or 0
        
        # Add to watchlist with higher display_order (appears first)
        new_item = PatientWatchlist(
            staff_id=staff_id,
            patient_id=patient_id,
            notes=notes,
            display_order=max_order + 1
        )
        
        db.session.add(new_item)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '已添加到特別關注',
            'watchlist_item': new_item.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'添加失敗: {str(e)}'}), 500


@admin_watchlist_bp.route('/<int:patient_id>', methods=['DELETE'])
@jwt_required()
def remove_from_watchlist(patient_id):
    """Remove a patient from watchlist"""
    try:
        staff_id = verify_admin()
        if not staff_id:
            return jsonify({'success': False, 'message': '無效的管理員權限'}), 403
        
        # Find watchlist item
        item = PatientWatchlist.query.filter_by(
            staff_id=staff_id,
            patient_id=patient_id
        ).first()
        
        if not item:
            return jsonify({'success': False, 'message': '此病人不在特別關注列表中'}), 404
        
        db.session.delete(item)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '已從特別關注中移除'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'移除失敗: {str(e)}'}), 500


@admin_watchlist_bp.route('/reorder', methods=['POST'])
@jwt_required()
def reorder_watchlist():
    """Reorder watchlist items"""
    try:
        staff_id = verify_admin()
        if not staff_id:
            return jsonify({'success': False, 'message': '無效的管理員權限'}), 403
        
        data = request.get_json()
        if not data or 'order' not in data:
            return jsonify({'success': False, 'message': '缺少排序資料'}), 400
        
        order_data = data['order']  # Expected: [{patient_id, display_order}, ...]
        
        # Update display_order for each item in a transaction
        for item_data in order_data:
            patient_id = item_data.get('patient_id')
            display_order = item_data.get('display_order')
            
            if patient_id is None or display_order is None:
                continue
            
            watchlist_item = PatientWatchlist.query.filter_by(
                staff_id=staff_id,
                patient_id=patient_id
            ).first()
            
            if watchlist_item:
                watchlist_item.display_order = display_order
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '排序已更新'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新排序失敗: {str(e)}'}), 500


@admin_watchlist_bp.route('/<int:patient_id>/notes', methods=['PUT'])
@jwt_required()
def update_watchlist_notes(patient_id):
    """Update notes for a watchlist patient"""
    try:
        staff_id = verify_admin()
        if not staff_id:
            return jsonify({'success': False, 'message': '無效的管理員權限'}), 403
        
        data = request.get_json()
        if not data or 'notes' not in data:
            return jsonify({'success': False, 'message': '缺少備註內容'}), 400
        
        # Find watchlist item
        item = PatientWatchlist.query.filter_by(
            staff_id=staff_id,
            patient_id=patient_id
        ).first()
        
        if not item:
            return jsonify({'success': False, 'message': '此病人不在特別關注列表中'}), 404
        
        item.notes = data['notes']
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '備註已更新',
            'watchlist_item': item.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失敗: {str(e)}'}), 500
