from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.config import config
from app.models import db
import os

def create_app(config_name='default'):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config[config_name])
    
    # 1. CORS：直接允許所有標頭 (萬用字元)
    # 注意：如果 supports_credentials=True，origins 不能用 "*"
    CORS(app, supports_credentials=True)

    db.init_app(app)
    jwt = JWTManager(app)
    
    # 2. 強力補強：手動反射任何請求過來的 Header
    @app.after_request
    def add_cors_headers(response):
        origin = request.headers.get('Origin')
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
        
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        
        # 關鍵：這裡把請求中所有的 Header 都准許通行
        allow_headers = request.headers.get('Access-Control-Request-Headers')
        if allow_headers:
            response.headers['Access-Control-Allow-Headers'] = allow_headers
        else:
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, ngrok-skip-browser-warning'
            
        response.headers['Access-Control-Allow-Methods'] = 'GET, PUT, POST, DELETE, OPTIONS'
        
        # 額外補上 ngrok 專用通行證
        response.headers['ngrok-skip-browser-warning'] = 'true'
        return response
    
    # --- 以下 Blueprint 註冊邏輯維持原樣 ---
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
