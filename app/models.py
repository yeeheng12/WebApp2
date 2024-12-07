from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager
from datetime import datetime
import re

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(200), nullable=True)  # Profile description
    posts = db.relationship('Post', backref='author', lazy=True, cascade="all, delete-orphan")
    followers = db.relationship(
        'User', secondary='follow',
        primaryjoin='Follow.followed_id == User.id',
        secondaryjoin='Follow.follower_id == User.id',
        backref=db.backref('following', lazy='dynamic'), lazy='dynamic'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_following(self, user):
        """Check if the current user is following another user."""
        return self.following.filter(Follow.followed_id == user.id).count() > 0

    def follow(self, user):
        """Follow another user."""
        if not self.is_following(user):
            follow = Follow(follower_id=self.id, followed_id=user.id)
            db.session.add(follow)

    def unfollow(self, user):
        """Unfollow another user."""
        follow = Follow.query.filter_by(follower_id=self.id, followed_id=user.id).first()
        if follow:
            db.session.delete(follow)

    def follower_count(self):
        """Count of followers."""
        return Follow.query.filter_by(followed_id=self.id).count()
        
    def post_count(self):
        """Returns the number of posts created by the user."""
        return Post.query.filter_by(user_id=self.id).count()

    def is_liking(self, post):
        """Check if the current user has liked a specific post."""
        return Like.query.filter_by(user_id=self.id, post_id=post.id).first() is not None

    def is_saving(self, post):
        """Check if the current user has saved a specific post."""
        return Save.query.filter_by(user_id=self.id, post_id=post.id).first() is not None

    def is_interacting(self, post, interaction_type):
        """Generic method to check if the user has liked or saved the post."""
        model = None
        if interaction_type == 'like':
            model = Like
        elif interaction_type == 'save':
            model = Save
        else:
            raise ValueError(f"Unknown interaction type: {interaction_type}")
        return model.query.filter_by(user_id=self.id, post_id=post.id).first() is not None

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tags = db.Column(db.String(255), nullable=True)  # Store hashtags as a comma-separated string

    # Explicit relationships for likes and saves
    liked_by = db.relationship('Like', backref='post', lazy='dynamic')
    saved_by = db.relationship('Save', backref='post', lazy='dynamic')
    comments = db.relationship('Comment', backref='post', lazy='dynamic')  # Added relationship

    def set_tags(self):
        """Extract hashtags from the content and store them in the tags field."""
        self.tags = ",".join(self.extract_hashtags())

    def extract_hashtags(self):
        """Extract hashtags from the content."""
        return re.findall(r"#(\w+)", self.content)  # Updated regex to capture hashtags more effectively

    def get_tags_list(self):
        """Return the tags as a list."""
        return self.tags.split(",") if self.tags else []

    def like_count(self):
        """Return the number of likes on this post. Optimized for efficiency."""
        return self.liked_by.count()  # Using count() for better performance over len()

    def save_count(self):
        """Return the number of saves on this post. Optimized for efficiency."""
        return self.saved_by.count()  # Using count() for better performance over len()

    def comment_count(self):
        """Return the number of comments on this post."""
        return self.comments.count()

class Follow(db.Model):
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.Index('ix_follow_follower_followed', 'follower_id', 'followed_id'),)  # Added composite index

class Like(db.Model):
    __tablename__ = 'likes'
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), primary_key=True, index=True)  # Added index
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True, index=True)  # Added index
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.Index('ix_likes_post_user', 'post_id', 'user_id'),)  # Added composite index

class Save(db.Model):
    __tablename__ = 'saves'
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), primary_key=True, index=True)  # Added index
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True, index=True)  # Added index
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.Index('ix_saves_post_user', 'post_id', 'user_id'),)  # Added composite index

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False, index=True)  # Added index
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)  # Added index

    user = db.relationship('User', backref='comments', lazy=True)
