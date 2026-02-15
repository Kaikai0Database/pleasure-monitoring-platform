from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app.models import db, Diary, User
from datetime import datetime, date
import json
import os

diary_bp = Blueprint('diary', __name__)

# 允許的圖片格式
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    """檢查檔案是否為允許的圖片格式"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@diary_bp.route('', methods=['GET'])
@jwt_required()
def get_diaries():
    """獲取使用者所有日記（依日期排序）"""
    try:
        current_user_id = int(get_jwt_identity())
        
        # 獲取查詢參數
        year = request.args.get('year', type=int)
        month = request.args.get('month', type=int)
        
        # 基本查詢
        query = Diary.query.filter_by(user_id=current_user_id)
        
        # 如果有年月篩選
        if year and month:
            # 篩選特定年月的日記
            from calendar import monthrange
            start_date = date(year, month, 1)
            last_day = monthrange(year, month)[1]
            end_date = date(year, month, last_day)
            query = query.filter(Diary.date >= start_date, Diary.date <= end_date)
        elif year:
            # 只篩選年份
            query = query.filter(db.extract('year', Diary.date) == year)
        
        # 依日期降序排序（最新的在前）
        diaries = query.order_by(Diary.date.desc()).all()
        
        return jsonify({
            'success': True,
            'diaries': [d.to_dict() for d in diaries]
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'獲取日記失敗: {str(e)}'}), 500


@diary_bp.route('/<date_str>', methods=['GET'])
@jwt_required()
def get_diary_by_date(date_str):
    """獲取特定日期的日記"""
    try:
        current_user_id = int(get_jwt_identity())
        
        # 解析日期字串 (格式: YYYY-MM-DD)
        diary_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # 查找日記
        diary = Diary.query.filter_by(user_id=current_user_id, date=diary_date).first()
        
        if not diary:
            return jsonify({'success': False, 'message': '該日期沒有日記'}), 404
        
        return jsonify({
            'success': True,
            'diary': diary.to_dict()
        }), 200
        
    except ValueError:
        return jsonify({'success': False, 'message': '日期格式錯誤，應為 YYYY-MM-DD'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': f'獲取日記失敗: {str(e)}'}), 500


@diary_bp.route('', methods=['POST'])
@jwt_required()
def create_diary():
    """創建新日記"""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # 驗證必要欄位 - 至少要有 mood 或 period_marker
        if not data or 'date' not in data:
            return jsonify({'success': False, 'message': '缺少日期欄位'}), 400
        
        if not data.get('mood') and not data.get('period_marker'):
            return jsonify({'success': False, 'message': '至少需要選擇心情或標記生理期'}), 400
        
        # 解析日期
        diary_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        
        # 允許同一天創建多筆日記（已移除重複檢查）
        
        # 創建新日記
        new_diary = Diary(
            user_id=current_user_id,
            date=diary_date,
            mood=data.get('mood'),  # 允許為 None
            content=data.get('content'),
            images=json.dumps(data.get('images', []), ensure_ascii=False),
            period_marker=data.get('period_marker', False)
        )
        
        db.session.add(new_diary)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'diary': new_diary.to_dict(),
            'message': '日記創建成功'
        }), 201
        
    except ValueError:
        return jsonify({'success': False, 'message': '日期格式錯誤，應為 YYYY-MM-DD'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'創建日記失敗: {str(e)}'}), 500


@diary_bp.route('/id/<int:diary_id>', methods=['GET'])
@jwt_required()
def get_diary_by_id(diary_id):
    """根據 ID 獲取日記"""
    try:
        current_user_id = int(get_jwt_identity())
        
        # 查找日記
        diary = Diary.query.get(diary_id)
        
        if not diary:
            return jsonify({'success': False, 'message': '日記不存在'}), 404
        
        # 檢查權限
        if diary.user_id != current_user_id:
            return jsonify({'success': False, 'message': '無權限查看此日記'}), 403
        
        return jsonify({
            'success': True,
            'diary': diary.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'獲取日記失敗: {str(e)}'}), 500


@diary_bp.route('/<int:diary_id>', methods=['PUT'])
@jwt_required()
def update_diary(diary_id):
    """更新日記"""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # 查找日記
        diary = Diary.query.get(diary_id)
        
        if not diary:
            return jsonify({'success': False, 'message': '日記不存在'}), 404
        
        # 檢查權限
        if diary.user_id != current_user_id:
            return jsonify({'success': False, 'message': '無權限修改此日記'}), 403
        
        # 更新欄位
        if 'mood' in data:
            diary.mood = data['mood']
        if 'content' in data:
            diary.content = data['content']
        if 'images' in data:
            diary.images = json.dumps(data['images'], ensure_ascii=False)
        if 'period_marker' in data:
            diary.period_marker = data['period_marker']
        
        diary.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'diary': diary.to_dict(),
            'message': '日記更新成功'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新日記失敗: {str(e)}'}), 500


@diary_bp.route('/<int:diary_id>', methods=['DELETE'])
@jwt_required()
def delete_diary(diary_id):
    """刪除日記"""
    try:
        current_user_id = int(get_jwt_identity())
        
        # 查找日記
        diary = Diary.query.get(diary_id)
        
        if not diary:
            return jsonify({'success': False, 'message': '日記不存在'}), 404
        
        # 檢查權限
        if diary.user_id != current_user_id:
            return jsonify({'success': False, 'message': '無權限刪除此日記'}), 403
        
        # 刪除關聯的圖片檔案
        if diary.images:
            try:
                images_list = json.loads(diary.images)
                upload_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'diary_images')
                for image_path in images_list:
                    file_path = os.path.join(upload_folder, os.path.basename(image_path))
                    if os.path.exists(file_path):
                        os.remove(file_path)
            except Exception as img_error:
                # 圖片刪除失敗不影響日記刪除
                print(f"刪除圖片失敗: {img_error}")
        
        db.session.delete(diary)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '日記已刪除'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'刪除日記失敗: {str(e)}'}), 500


@diary_bp.route('/upload-image', methods=['POST'])
@jwt_required()
def upload_image():
    """上傳圖片"""
    try:
        current_user_id = int(get_jwt_identity())
        
        # 檢查是否有檔案
        if 'images' not in request.files:
            return jsonify({'success': False, 'message': '沒有上傳檔案'}), 400
        
        files = request.files.getlist('images')
        
        if not files or all(f.filename == '' for f in files):
            return jsonify({'success': False, 'message': '沒有選擇檔案'}), 400
        
        uploaded_paths = []
        upload_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'diary_images')
        
        # 確保上傳資料夾存在
        os.makedirs(upload_folder, exist_ok=True)
        
        for file in files:
            if file and allowed_file(file.filename):
                # 生成安全的檔案名稱（加上時間戳避免重複）
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
                name, ext = os.path.splitext(filename)
                unique_filename = f"{current_user_id}_{timestamp}_{name}{ext}"
                
                file_path = os.path.join(upload_folder, unique_filename)
                file.save(file_path)
                
                # 返回相對路徑
                uploaded_paths.append(f"/uploads/diary_images/{unique_filename}")
            else:
                return jsonify({
                    'success': False, 
                    'message': f'檔案格式不支援: {file.filename}。僅支援 png, jpg, jpeg, gif, webp'
                }), 400
        
        return jsonify({
            'success': True,
            'images': uploaded_paths,
            'message': f'成功上傳 {len(uploaded_paths)} 張圖片'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'上傳圖片失敗: {str(e)}'}), 500
