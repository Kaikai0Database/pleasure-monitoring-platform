from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.config import config
from app.models import db
import os

def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__, instance_relative_config=True)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    #CORS 設定
    # 這裡我們不寫 "*"，讓它保持彈性
    CORS(app, supports_credentials=True)

    db.init_app(app)
    jwt = JWTManager(app)
    
    # 解決 credentials + dynamic origin 的關鍵
    @app.after_request
    def add_cors_headers(response):
        origin = request.headers.get('Origin')
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
            
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
        
        # 原有的其他 Header
        response.headers['ngrok-skip-browser-warning'] = 'true'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        return response
    
    # JWT error handlers
    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        return jsonify({'success': False, 'message': '無效的token'}), 401
    
    @jwt.unauthorized_loader
    def unauthorized_callback(error_string):
        return jsonify({'success': False, 'message': '缺少Authorization header'}), 401
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'success': False, 'message': 'Token已過期，請重新登入'}), 401
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({'success': False, 'message': 'Token已被撤銷'}), 401
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.history import history_bp
    from app.routes.diary import diary_bp
    from app.routes.alerts import alerts_bp
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
    app.register_blueprint(admin_auth_bp, url_prefix='/api/admin/auth')
    app.register_blueprint(admin_patients_bp, url_prefix='/api/admin/patients')
    app.register_blueprint(admin_watchlist_bp, url_prefix='/api/admin/watchlist')
    app.register_blueprint(admin_dashboard_bp, url_prefix='/api/admin/dashboard')
    app.register_blueprint(admin_diary_bp, url_prefix='/api/admin/diary')
    app.register_blueprint(admin_assignments_bp, url_prefix='/api/admin/assignments')

    @app.route('/uploads/diary_images/<filename>')
    def uploaded_file(filename):
        upload_folder = os.path.join(os.path.dirname(__file__), 'uploads', 'diary_images')
        return send_from_directory(upload_folder, filename)
    
    with app.app_context():
        db.create_all()
    
    @app.route('/api/health')
    def health_check():
        return {'status': 'ok', 'message': 'Flask backend is running'}
    
    return app
