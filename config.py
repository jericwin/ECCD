import os
import urllib.parse

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'eccd-development-secret-key-12345')

    # Database Configuration: support DATABASE_URL / MYSQL_URL or individual env vars
    db_url = os.environ.get('DATABASE_URL') or os.environ.get('MYSQL_URL')
    if db_url:
        parsed = urllib.parse.urlparse(db_url)
        DB_HOST = parsed.hostname or 'localhost'
        DB_PORT = int(parsed.port or 3306)
        DB_USER = parsed.username or 'root'
        DB_PASSWORD = urllib.parse.unquote(parsed.password or '')
        DB_NAME = parsed.path.lstrip('/') if parsed.path else 'eccd_db'
        DB_SSL = ('ssl' in parsed.query.lower()) or (os.environ.get('DB_SSL', 'true').lower() in ('1', 'true', 'yes'))
    else:
        DB_HOST = os.environ.get('DB_HOST', 'localhost')
        DB_PORT = int(os.environ.get('DB_PORT', 3306))
        DB_USER = os.environ.get('DB_USER', 'root')
        DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
        DB_NAME = os.environ.get('DB_NAME', 'eccd_db')
        DB_SSL = os.environ.get('DB_SSL', 'false').lower() in ('1', 'true', 'yes')

    CA_PATH = os.environ.get('CA_PATH', None)

    # Base and Upload directories
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    BUNDLED_UPLOADS = os.path.join(BASE_DIR, "uploads")
    # In Vercel serverless functions, root filesystem is read-only; use /tmp for dynamic uploads
    if os.environ.get('VERCEL'):
        UPLOAD_FOLDER = os.path.join('/tmp', 'uploads')
    else:
        UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', os.path.join(BASE_DIR, "uploads"))

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024