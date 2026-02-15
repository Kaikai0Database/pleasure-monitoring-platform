from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, ScoreAlert
from datetime import datetime

alerts_bp = Blueprint('alerts', __name__)

@alerts_bp.route('', methods=['GET'])
@jwt_required()
def get_alerts():
    """Get user's all alerts"""
    try:
        current_user_id = int(get_jwt_identity())
        
        # Get all alerts for user, ordered by date descending
        alerts = ScoreAlert.query.filter_by(
            user_id=current_user_id
        ).order_by(ScoreAlert.alert_date.desc()).all()
        
        return jsonify({
            'success': True,
            'alerts': [alert.to_dict() for alert in alerts]
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'獲取警告失敗: {str(e)}'}), 500


@alerts_bp.route('/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    """Get count of unread alerts"""
    try:
        current_user_id = int(get_jwt_identity())
        
        count = ScoreAlert.query.filter_by(
            user_id=current_user_id,
            is_read=False
        ).count()
        
        return jsonify({
            'success': True,
            'count': count
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'獲取未讀數量失敗: {str(e)}'}), 500


@alerts_bp.route('/<int:alert_id>/read', methods=['PUT'])
@jwt_required()
def mark_as_read(alert_id):
    """Mark alert as read"""
    try:
        current_user_id = int(get_jwt_identity())
        
        # Find alert
        alert = ScoreAlert.query.get(alert_id)
        
        if not alert:
            return jsonify({'success': False, 'message': '警告不存在'}), 404
        
        # Check permission
        if alert.user_id != current_user_id:
            return jsonify({'success': False, 'message': '無權限'}), 403
        
        # Mark as read
        alert.is_read = True
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '已標記為已讀'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'標記失敗: {str(e)}'}), 500


@alerts_bp.route('/mark-all-read', methods=['PUT'])
@jwt_required()
def mark_all_read():
    """Mark all alerts as read"""
    try:
        current_user_id = int(get_jwt_identity())
        
        # Get all unread alerts
        alerts = ScoreAlert.query.filter_by(
            user_id=current_user_id,
            is_read=False
        ).all()
        
        # Mark all as read
        for alert in alerts:
            alert.is_read = True
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'已標記 {len(alerts)} 個警告為已讀'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'標記失敗: {str(e)}'}), 500
