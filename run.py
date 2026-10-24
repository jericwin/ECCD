from flask import Flask, request, send_from_directory, session
import os
from config import Config
from routes.main import main_bp
from routes.auth import auth_bp
from routes.teacher import teacher_bp
from routes.parent import parent_bp
from routes.chat import chat_bp
from routes.provincial import provincial_bp
from routes.municipality import municipality_bp
from routes.school import school_bp
from routes.superadmin import superadmin_bp

def create_app():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, 'templates'),
        static_folder=os.path.join(base_dir, 'static')
    )
    app.config.from_object(Config)
    
    # Configure logging
    import logging
    import sys
    
    app.logger.handlers.clear()
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')

    if os.environ.get('VERCEL'):
        # On Vercel, log to stdout so logs are visible in the Vercel dashboard
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(logging.INFO)
        app.logger.addHandler(stream_handler)
        
        db_logger = logging.getLogger('db')
        db_logger.handlers.clear()
        db_logger.addHandler(stream_handler)
        db_logger.setLevel(logging.INFO)
    else:
        from logging.handlers import RotatingFileHandler
        try:
            file_handler = RotatingFileHandler('app.log', maxBytes=10000000, backupCount=3)
            file_handler.setFormatter(formatter)
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            
            db_logger = logging.getLogger('db')
            db_logger.handlers.clear()
            db_logger.addHandler(file_handler)
            db_logger.setLevel(logging.INFO)
        except Exception:
            stream_handler = logging.StreamHandler(sys.stdout)
            stream_handler.setFormatter(formatter)
            app.logger.addHandler(stream_handler)
    
    app.logger.setLevel(logging.INFO)
    
    # Ensure upload directories exist safely
    subfolders = ['teachers', 'learners', 'classrooms', 'posts', 'classwork', 'certificates', 'submissions']
    for sf in subfolders:
        try:
            os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], sf), exist_ok=True)
        except Exception as e:
            app.logger.warning(f"Could not create upload directory for {sf}: {e}")
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(parent_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(provincial_bp)
    app.register_blueprint(municipality_bp)
    app.register_blueprint(school_bp)
    app.register_blueprint(superadmin_bp)
    
    @app.context_processor
    def inject_global_notifications():
        if 'user_id' in session:
            from db import execute_query
            user_id = session['user_id']
            notifications = execute_query(
                "SELECT * FROM notifications WHERE user_id = %s AND is_read = FALSE ORDER BY created_at DESC",
                (user_id,),
                fetch_all=True
            ) or []
            return dict(unread_notifications=notifications)
        return dict(unread_notifications=[])
    
    # Override static uploads handler to serve from dynamic upload folder or fallback to bundled uploads
    @app.route('/static/uploads/<path:filename>')
    def serve_uploads(filename):
        # 1. Check dynamic uploads folder (e.g. /tmp/uploads on Vercel or local uploads)
        dynamic_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(dynamic_path):
            return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

        # 2. Check bundled uploads folder in the repository (e.g. landing videos)
        bundled_folder = os.path.join(base_dir, 'uploads')
        bundled_path = os.path.join(bundled_folder, filename)
        if os.path.exists(bundled_path):
            return send_from_directory(bundled_folder, filename)

        from flask import abort
        abort(404)
        
    @app.before_request
    def log_request():
        app.logger.info(f"HTTP_REQUEST: {request.method} {request.path} | Args: {dict(request.args)} | User-Agent: {request.headers.get('User-Agent')}")
    
    # Add static files browser caching header and response logging
    @app.after_request
    def add_header(response):
        app.logger.info(f"HTTP_RESPONSE: {request.method} {request.path} -> Status {response.status}")
        if request.path.startswith('/static/'):
            if request.path.startswith('/static/uploads/'):
                # Force browser to always fetch user uploads/avatars fresh
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response.headers['Pragma'] = 'no-cache'
                response.headers['Expires'] = '0'
            else:
                # Cache standard css, js, fonts for 1 year
                response.cache_control.max_age = 31536000
                response.cache_control.public = True
        return response
        
    return app

if __name__ == '__main__':
    app = create_app()
    print("Starting ECCD Monitoring System...")
    print("Visit http://127.0.0.1:5000/ to view the application.")
    app.run(host='127.0.0.1', port=5000, debug=True, threaded=True, use_reloader=False)
