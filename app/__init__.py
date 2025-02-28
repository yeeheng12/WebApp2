from flask import Flask, request, session, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

# Initialize Flask app
app = Flask(__name__)
app.config.from_object('config')  # Load configurations from config.py
csrf = CSRFProtect(app)

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Set the login view for @login_required
login_manager.login_message = "Please log in to access this page."

# Import views and models
from app import views, models

@login_manager.user_loader
def load_user(user_id):
    try:
        return models.User.query.get(int(user_id))
    except (ValueError, TypeError):
        return None
