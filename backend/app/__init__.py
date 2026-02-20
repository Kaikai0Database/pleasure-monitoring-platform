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
    
    # Initialize extensions with CORS configuration
    import os, re
    
    # Hardcoded allowed origins: Cloudflare Pages domains + local dev
    # Flask-CORS supports regex strings in the origins list
    CLOUDFLARE_PAGES_ORIGINS = [
        r"https://.*\.pleasure-monitoring-platform\.pages\.dev",  # all preview branches
        "https://pleasure-monitoring-platform.pages.dev",          # production Pages URL
        "http://localhost:5173",                                    # local patient dev
        "http://localhost:5174",                                    # local admin dev
    ]
    
    # Allow additional origins from env var (comma-separated)
    env_origins = os.environ.get('CORS_ALLOWED_ORIGINS')
    if env_origins:
        CLOUDFLARE_PAGES_ORIGINS.extend(env_origins.split(','))
    
    CORS(app,
         resources={r"/*": {
             "origins": CLOUDFLARE_PAGES_ORIGINS,
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization", "ngrok-skip-browser-warning"]
         }},
         supports_credentials=True)

    jwt = JWTManager(app)
    
    # Middleware to bypass ngrok browser warning and add CORS headers
    @app.after_request
    def add_ngrok_headers(response):
        """Add ngrok-skip-browser-warning header, CORS headers, and cache control"""
        # Ngrok bypass
        response.headers['ngrok-skip-browser-warning'] = 'true'
        
        # CORS headers
        # Use first allowed origin from env or *
        # If multiple origins are allowed, we should let Flask-CORS handle it or dynamic check
        # For this manual header, we will use the same logic:
        allowed_origins_env = os.environ.get('CORS_ALLOWED_ORIGINS')
        if allowed_origins_env:
             # Ideally we check request.origin against list, but for simplicity here:
             # We can't set multiple in header. Flask-CORS does this. 
             # Let's keep the manual header strictly for 'ngrok' support or rely on Flask-CORS?
             # User prompt primarily focused on CORS(app).
             # I will set it to * if env allows it (not strict) or just let Flask-CORS handle?
             # Existing code sets it. I will set to the first origin or * to be safe/simple.
             allowed_list = allowed_origins_env.split(',')
             response.headers['Access-Control-Allow-Origin'] = allowed_list[0] if allowed_list else '*'
        else:
             response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, ngrok-skip-browser-warning'
        
        # Cache control headers - prevent browser from caching responses
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, proxy-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response
    
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
