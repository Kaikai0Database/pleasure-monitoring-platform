from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.config import config
from app.models import db

def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__, instance_relative_config=True)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions with more explicit CORS configuration
    CORS(app, 
         origins='*',
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    db.init_app(app)
    jwt = JWTManager(app)
    
    # JWT error handlers
    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        print(f"❌ Invalid token error: {error_string}")
        return jsonify({
            'success': False,
            'message': '無效的token'
        }), 401
    
    @jwt.unauthorized_loader
    def unauthorized_callback(error_string):
        print(f"❌ Unauthorized error: {error_string}")
        return jsonify({
            'success': False,
            'message': '缺少Authorization header'
        }), 401
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        print(f"❌ Expired token: {jwt_payload}")
        return jsonify({
            'success': False,
            'message': 'Token已過期，請重新登入'
        }), 401
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        print(f"❌ Revoked token: {jwt_payload}")
        return jsonify({
            'success': False,
            'message': 'Token已被撤銷'
        }), 401
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.history import history_bp
    from app.routes.diary import diary_bp
    from app.routes.alerts import alerts_bp
    
    # Admin blueprints
    from app.routes.admin_auth import admin_auth_bp
    from app.routes.admin_patients import admin_patients_bp
    from app.routes.admin_watchlist import admin_watchlist_bp
    from app.routes.admin_dashboard import admin_dashboard_bp
    from app.routes.admin_diary import admin_diary_bp
    from app.routes.admin_assignments import admin_assignments_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(history_bp, url_prefix='/api/history')
    app.register_blueprint(diary_bp, url_prefix='/api/diary')
    app.register_blueprint(alerts_bp, url_prefix='/api/alerts')
    
    # Admin routes
    app.register_blueprint(admin_auth_bp, url_prefix='/api/admin/auth')
    app.register_blueprint(admin_patients_bp, url_prefix='/api/admin/patients')
    app.register_blueprint(admin_watchlist_bp, url_prefix='/api/admin/watchlist')
    app.register_blueprint(admin_dashboard_bp, url_prefix='/api/admin/dashboard')
    app.register_blueprint(admin_diary_bp, url_prefix='/api/admin/diary')
    app.register_blueprint(admin_assignments_bp, url_prefix='/api/admin/assignments')

    
    # 提供上傳圖片的靜態檔案服務
    from flask import send_from_directory
    import os
    
    @app.route('/uploads/diary_images/<filename>')
    def uploaded_file(filename):
        # 圖片存儲在 backend/app/uploads/diary_images
        upload_folder = os.path.join(os.path.dirname(__file__), 'uploads', 'diary_images')
        print(f"[INFO] Trying to serve image from: {upload_folder}/{filename}")
        
        # 檢查檔案是否存在
        full_path = os.path.join(upload_folder, filename)
        if not os.path.exists(full_path):
            print(f"[ERROR] File not found: {full_path}")
            return jsonify({'error': 'File not found'}), 404
        
        print(f"[SUCCESS] Serving file: {full_path}")
        return send_from_directory(upload_folder, filename)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    @app.route('/api/health')
    def health_check():
        return {'status': 'ok', 'message': 'Flask backend is running'}
    
    return app
