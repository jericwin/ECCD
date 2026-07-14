from flask import Flask, request, send_from_directory
import os
from config import Config
from routes.main import main_bp
from routes.auth import auth_bp
from routes.teacher import teacher_bp
from routes.parent import parent_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Configure file logging
    import logging
    from logging.handlers import RotatingFileHandler
    
    file_handler = RotatingFileHandler('app.log', maxBytes=10000000, backupCount=3)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s'
    ))
    file_handler.setLevel(logging.INFO)
    
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    
    db_logger = logging.getLogger('db')
    db_logger.addHandler(file_handler)
    db_logger.setLevel(logging.INFO)
    
    # Ensure upload directories exist
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'teachers'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'learners'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'classrooms'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'posts'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'classwork'), exist_ok=True)
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(parent_bp)
    
    # Override static uploads handler to serve from unsynced folder
    @app.route('/static/uploads/<path:filename>')
    def serve_uploads(filename):
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        app.logger.info(f"Serve Upload: {filename} from {path} | Exists: {os.path.exists(path)}")
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
        
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
