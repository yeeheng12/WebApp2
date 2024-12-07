from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError, EqualTo, Regexp
from wtforms.file import FileField, FileRequired, FileAllowed
from .models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20), Regexp('^[a-zA-Z0-9_.-]*$', message="Username must contain only letters, numbers, dots, underscores, and hyphens.")])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is already taken.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')  # Add a boolean field for "remember me"
    submit = SubmitField('Login')

class PostForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired()])
    image = FileField('Image', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')  # Restrict file types for post images
    ])
    submit = SubmitField('Create Post')

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    description = TextAreaField('Description', validators=[Length(max=200)])
    password = PasswordField('New Password (optional)', validators=[Length(min=6), EqualTo('confirm_password', message="Passwords must match.")])
    confirm_password = PasswordField('Confirm New Password')
    avatar = FileField('Avatar Image', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')  # Restrict file types for avatar images
    ])
    submit = SubmitField('Update Profile')

    def validate_username(self, username):
        # Ensure the username is unique
        user = User.query.filter_by(username=username.data).first()
        if user and user.username != self.username.data:
            raise ValidationError('This username is already taken. Please choose a different one.')

    def validate_password(self, password):
        if password.data and len(password.data) < 6:
            raise ValidationError("Password must be at least 6 characters long.")

class SearchForm(FlaskForm):
    query = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')

class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Post Comment')
