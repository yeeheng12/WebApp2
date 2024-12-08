from flask import Flask, request, session, render_template
from flask_admin import Admin
from flask_babel import Babel
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

def get_locale():
    if request.args.get('lang'):
        session['lang'] = request.args.get('lang')
    return session.get('lang', 'en')

# Initialize Flask app
app = Flask(__name__)
app.config.from_object('config')  # Load configurations from config.py
csrf = CSRFProtect(app)

# Initialize extensions
db = SQLAlchemy(app)
babel = Babel(app, locale_selector=get_locale)
admin = Admin(app, template_mode='bootstrap4')
migrate = Migrate(app, db)

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Set the login view for @login_required
login_manager.login_message = "Please log in to access this page."

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()  # Rollback any pending transactions
    return render_template('500.html'), 500

# Import views and models
from app import views, models

@login_manager.user_loader
def load_user(user_id):
    try:
        return models.User.query.get(int(user_id))
    except (ValueError, TypeError):
        return None
