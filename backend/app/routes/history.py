from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, AssessmentHistory, User
from app.admin_models import PatientAssignment, PatientWatchlist, HealthcareStaff
from sqlalchemy import desc
from datetime import datetime
import json

history_bp = Blueprint('history', __name__)

@history_bp.route('', methods=['GET'])
@jwt_required()
def get_history():
    """Get user's assessment history (active only)"""
    try:
        current_user_id = int(get_jwt_identity())
        
        # Auto-delete records older than 10 days in trash
        try:
            from datetime import timedelta
            ten_days_ago = datetime.now() - timedelta(days=10)
            
            # Find old trash items
            old_trash = AssessmentHistory.query.filter(
                AssessmentHistory.is_deleted == True,
                AssessmentHistory.deleted_at < ten_days_ago
            ).all()
            
            # Delete them permanently
            for item in old_trash:
                db.session.delete(item)
            
            if old_trash:
                db.session.commit()
        except Exception as e:
            print(f"Auto-cleanup failed: {e}")

        # Get active history (not deleted)
        histories = AssessmentHistory.query.filter_by(
            user_id=current_user_id,
            is_deleted=False
        ).order_by(AssessmentHistory.completed_at.desc()).all()
        
        return jsonify({
            'success': True,
            'history': [h.to_dict() for h in histories]
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'獲取歷史記錄失敗: {str(e)}'}), 500


@history_bp.route('/trash', methods=['GET'])
@jwt_required()
def get_trash():
    """Get user's deleted history (recycle bin)"""
    try:
        current_user_id = int(get_jwt_identity())
        
        # Get deleted history
        trash_items = AssessmentHistory.query.filter_by(
            user_id=current_user_id,
            is_deleted=True
        ).order_by(AssessmentHistory.deleted_at.desc()).all()
        
        return jsonify({
            'success': True,
            'history': [h.to_dict() for h in trash_items]
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'獲取回收桶失敗: {str(e)}'}), 500


@history_bp.route('', methods=['POST'])
@jwt_required()
def save_history():
    """Save new assessment result"""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # Validate input
        if not data or not all(key in data for key in ['total_score', 'max_score', 'answers']):
            return jsonify({'success': False, 'message': '缺少必要欄位'}), 400
        
        # Get user to determine group
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({'success': False, 'message': '找不到用戶'}), 404
        
        # Determine level based on user group
        total_score = data['total_score']
        if user.group == 'student':
            # Student group: threshold is 23
            level = '需要關注' if total_score >= 23 else '良好'
        else:
            # Clinical group: threshold is 29
            level = '需要關注' if total_score >= 29 else '良好'
        
        # Create new history record
        new_history = AssessmentHistory(
            user_id=current_user_id,
            total_score=total_score,
            max_score=data['max_score'],
            level=level,
            answers=json.dumps(data['answers'], ensure_ascii=False),
            completed_at=datetime.now()
        )
        
        db.session.add(new_history)
        db.session.commit()
        
        # --- Auto-Watchlist Logic ---
        # Check thresholds: Student >= 23, Clinical >= 29
        threshold_met = False
        if user.group == 'student' and total_score >= 23:
            threshold_met = True
        elif user.group == 'clinical' and total_score >= 29:
            threshold_met = True
            
        if threshold_met:
            try:
                # Find target staff to notify
                target_staff_ids = []
                
                # 1. Check assigned staff
                assignments = PatientAssignment.query.filter_by(patient_id=current_user_id).all()
                if assignments:
                    target_staff_ids = [a.staff_id for a in assignments]
                
                # 2. If no assignments, fallback to Super Admin
                if not target_staff_ids:
                    super_admin = HealthcareStaff.query.filter_by(role='super_admin').first()
                    if super_admin:
                        target_staff_ids.append(super_admin.id)
                
                # 3. Add to watchlist for each target staff
                for staff_id in target_staff_ids:
                    # Check if already in watchlist
                    exists = PatientWatchlist.query.filter_by(
                        staff_id=staff_id,
                        patient_id=current_user_id
                    ).first()
                    
                    if not exists:
                        # Get max display order
                        max_order = db.session.query(
                            db.func.max(PatientWatchlist.display_order)
                        ).filter_by(staff_id=staff_id).scalar() or 0
                        
                        new_watchlist = PatientWatchlist(
                            staff_id=staff_id,
                            patient_id=current_user_id,
                            notes=f"自動關注：分數達標 ({total_score}分 - {user.group})",
                            display_order=max_order + 1
                        )
                        db.session.add(new_watchlist)
                        print(f"Auto-added user {current_user_id} to staff {staff_id} watchlist due to high score {total_score}")
                
                db.session.commit()
            except Exception as w_err:
                print(f"Auto-watchlist failed: {w_err}")
                # Don't fail the request, just log error
        # ----------------------------
        
        # Check and create alerts if needed (both high and low score alerts)
        try:
            from app.utils.alert_utils import check_and_create_alert
            alerts = check_and_create_alert(current_user_id, new_history.completed_at.date())
            if alerts:
                for alert in alerts:
                    print(f"{alert.alert_type.upper()} alert created for user {current_user_id} on {alert.alert_date}")
        except Exception as alert_error:
            print(f"Alert check failed: {alert_error}")
            # Don't fail the main request if alert check fails
        
        return jsonify({
            'success': True,
            'history_id': new_history.id,
            'level': level,  # Return the calculated level
            'message': '評估結果已保存'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'保存失敗: {str(e)}'}), 500


@history_bp.route('/<int:history_id>', methods=['DELETE'])
@jwt_required()
def delete_history(history_id):
    """Soft delete a history record"""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json() or {}
        delete_reason = data.get('reason', '未指定原因')
        permanent = data.get('permanent', False)
        
        # Find history record
        history = AssessmentHistory.query.get(history_id)
        
        if not history:
            return jsonify({'success': False, 'message': '記錄不存在'}), 404
        
        # Check permission
        if history.user_id != current_user_id:
            return jsonify({'success': False, 'message': '無權限刪除此記錄'}), 403
        
        if permanent:
            # Permanent delete (for restoring from trash or emptying trash)
            db.session.delete(history)
            message = '記錄已永久刪除'
        else:
            # Soft delete
            history.is_deleted = True
            history.deleted_at = datetime.now()
            history.delete_reason = delete_reason
            message = '記錄已移至回收桶'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': message
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'刪除失敗: {str(e)}'}), 500


@history_bp.route('/<int:history_id>/restore', methods=['POST'])
@jwt_required()
def restore_history(history_id):
    """Restore a deleted history record"""
    try:
        current_user_id = int(get_jwt_identity())
        
        # Find history record
        history = AssessmentHistory.query.get(history_id)
        
        if not history:
            return jsonify({'success': False, 'message': '記錄不存在'}), 404
        
        # Check permission
        if history.user_id != current_user_id:
            return jsonify({'success': False, 'message': '無權限操作此記錄'}), 403
            
        history.is_deleted = False
        history.deleted_at = None
        history.delete_reason = None
        
        # Get user to determine group threshold
        user = User.query.get(current_user_id)
        
        # Recalculate level based on total score and user group upon restoration
        if user and user.group == 'student':
            # Student group: threshold is 23
            history.level = '需要關注' if history.total_score >= 23 else '良好'
        else:
            # Clinical group: threshold is 29
            history.level = '需要關注' if history.total_score >= 29 else '良好'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '記錄已還原'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'還原失敗: {str(e)}'}), 500
