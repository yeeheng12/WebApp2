import os

# Security
WTF_CSRF_ENABLED = True
SECRET_KEY = 'a-very-secret-key'
PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes (value in seconds)
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
SESSION_COOKIE_SAMESITE = 'Lax'

# Database
basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False  # Prevent unnecessary overhead

# Internationalization and Localization
BABEL_DEFAULT_LOCALE = 'en'
BABEL_SUPPORTED_LOCALES = ['en', 'es', 'fr', 'de']

# Flask-Admin UI settings
FLASK_ADMIN_SWATCH = 'cerulean'

# Preferred URL scheme
PREFERRED_URL_SCHEME = 'https'  # Use HTTPS for URL generation in production

# File Upload Settings
UPLOAD_FOLDER = os.path.join(basedir, 'app/static/images/uploads')  # Directory for uploaded files
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}  # Allowed file extensions
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max file size


