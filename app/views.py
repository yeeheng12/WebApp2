import os
from werkzeug.utils import secure_filename
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .forms import RegistrationForm, LoginForm, PostForm, EditProfileForm, SearchForm, CommentForm
from .models import User, Post, Comment, Like, Save
from . import db
from app import app
from datetime import datetime

# Set the upload folder paths for user avatars and post images
app.config['UPLOAD_FOLDER'] = 'app/static/images/uploads'
app.config['DEFAULT_AVATAR_FOLDER'] = 'app/static/images/default'
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max file size (16MB)

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            remember = form.remember_me.data
            login_user(user, remember=remember)
            next_page = request.args.get('next')  # Get the "next" URL if available
            return redirect(next_page or url_for('home'))  # Redirect to "next" or default to home
        flash("Login unsuccessful. Check username and password.", "danger")
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def home():
    # Fetch posts from the database
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('index.html', posts=posts)

@app.route('/profile/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    edit_mode = request.args.get('edit') == '1' and user.id == current_user.id
    form = EditProfileForm(obj=user)
    
    # Get the posts created by the user
    posts = Post.query.filter_by(user_id=user.id).all()

    return render_template(
        'profile.html',
        user=user,
        followers=user.follower_count(),
        following=user.following_count(),
        post_count=user.post_count(),
        form=form,
        edit_mode=edit_mode,
        posts=posts  # Pass the user's posts to the template
    )

@app.route('/edit_profile', methods=['POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        # Check if the username is unique
        if form.username.data != current_user.username:
            user_with_new_username = User.query.filter_by(username=form.username.data).first()
            if user_with_new_username:
                flash('This username is already taken. Please choose a different one.', 'danger')
                return redirect(url_for('profile', username=current_user.username, edit=1))

        # Check if password is being changed
        if form.password.data:
            current_user.password_hash = generate_password_hash(form.password.data)

        # Handle avatar upload
        avatar = form.avatar.data
        if avatar and allowed_file(avatar.filename):
            filename = secure_filename(avatar.filename)
            avatar.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))  # Save the image
            current_user.avatar = filename  # Update avatar path

        # Update the user's information
        current_user.username = form.username.data
        current_user.description = form.description.data
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('profile', username=current_user.username))
    
    flash('Error updating profile. Please try again.', 'danger')
    return redirect(url_for('profile', username=current_user.username, edit=1))

@app.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        content = form.content.data
        image = form.image.data

        if image:
            if allowed_file(image.filename):
                try:
                    filename = secure_filename(image.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    image.save(filepath)  # Save the file to the uploads folder
                    flash(f"Image successfully uploaded to {filepath}", 'success')
                except Exception as e:
                    flash(f"Error saving image: {e}", 'danger')
                    filename = None
            else:
                flash("Invalid file type. Only jpg, jpeg, and png are allowed.", 'danger')
                filename = None
        else:
            filename = None

        # Save the post
        new_post = Post(content=content, author=current_user, image=filename)
        db.session.add(new_post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))

    return render_template('create_post.html', form=form)

@app.route('/view_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()

    # Handle the comment form submission
    if form.validate_on_submit():
        comment = Comment(
            content=form.content.data,
            post_id=post.id,
            user_id=current_user.id
        )
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been added!', 'success')

        # Return updated comment count and comment details as JSON
        return jsonify({
            'content': comment.content,
            'user': comment.user.username,
            'timestamp': comment.timestamp.strftime('%b %d, %Y %H:%M'),
            'comment_count': post.comment_count()
        })
    
    # Render post and comments in the background for modal toggle
    if request.is_xhr:  # This ensures that the request was made via AJAX
        comments = post.comments
        return render_template('comments_modal.html', post=post, comments=comments, form=form)

    return render_template('post.html', post=post, form=form)


@app.route('/like/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    like = Like.query.filter_by(post_id=post.id, user_id=current_user.id).first()

    if like:
        db.session.delete(like)
        liked = False
    else:
        db.session.add(Like(post_id=post.id, user_id=current_user.id))
        liked = True

    db.session.commit()

    # Get updated like count
    like_count = post.like_count()

    return jsonify({
        'liked': liked,
        'like_count': like_count  # Return the updated like count
    })

@app.route('/save_toggle/<int:post_id>', methods=['POST'])
@login_required
def save_toggle(post_id):
    post = Post.query.get_or_404(post_id)
    save = Save.query.filter_by(post_id=post.id, user_id=current_user.id).first()

    if save:
        db.session.delete(save)
        saved = False
    else:
        db.session.add(Save(post_id=post.id, user_id=current_user.id))
        saved = True

    db.session.commit()

    return jsonify({'saved': saved})

@app.route('/add_comment/<int:post_id>', methods=['POST'])
@login_required
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    content = request.json.get('content')
    if not content:
        return jsonify({'error': 'Content cannot be empty.'}), 400

    # Add the comment to the post
    comment = Comment(content=content, user=current_user, post=post)
    db.session.add(comment)
    db.session.commit()

    # Get updated comment count
    comment_count = post.comment_count()

    return jsonify({
        'user': current_user.username,
        'content': comment.content,
        'timestamp': comment.timestamp.strftime('%Y-%m-%d %H:%M'),
        'comment_count': comment_count  # Return the updated comment count
    })

@app.route('/saved_posts', methods=['GET'])
@login_required
def view_saved_posts():
    # Get all posts saved by the current user
    saved_posts = [save.post for save in current_user.saves]
    return render_template('saved_posts.html', posts=saved_posts)

# views.py
from flask import render_template, request, jsonify
from flask_login import login_required
from .models import User, Post
from .forms import SearchForm

from flask import jsonify, request
from app.models import User, Post

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '').strip().lower()  # Get the search query
    if not query:
        return jsonify([])  # Return an empty list if no query provided

    results = []

    # Check if the query starts with a hashtag
    if query.startswith('#'):
        # Search for posts with hashtags matching the query
        posts = Post.query.filter(Post.tags.ilike(f"%{query[1:]}%")).all()
        results = [
            {
                'type': 'hashtag',
                'content': f"#{tag}",
                'post_link': url_for('post', post_id=post.id),
            }
            for post in posts
            for tag in post.get_tags_list() if tag.startswith(query[1:])
        ]
    else:
        # Search users based on the query
        users = User.query.filter(User.username.ilike(f"%{query}%")).all()
        results = [
            {
                'type': 'user',
                'username': user.username,
                'avatar': user.get_avatar(),
                'profile_link': url_for('profile', username=user.username),
            }
            for user in users
        ]

    return jsonify(results)  # Return JSON response

@app.route('/follow_toggle/<int:user_id>', methods=['POST'])
@login_required
def follow_toggle(user_id):
    user = User.query.get_or_404(user_id)

    # Toggle follow/unfollow status
    if current_user.is_following(user):
        current_user.unfollow(user)  # Removes the follow relationship
        follow_state = 'follow'  # Indicating user is now unfollowing
    else:
        current_user.follow(user)  # Creates the follow relationship
        follow_state = 'unfollow'  # Indicating user is now following

    # Commit the changes to the database
    db.session.commit()

    # Return updated follower and following counts
    return jsonify({
        'follow_state': follow_state,
        'followers_count': user.followers.count(),
        'following_count': user.following.count()
    })

@app.route('/load_more_comments/<int:post_id>', methods=['GET'])
@login_required
def load_more_comments(post_id):
    post = Post.query.get_or_404(post_id)
    
    # Paginate comments (show 5 more per request)
    page = request.args.get('page', 1, type=int)
    comments = post.comments.paginate(page, 5, False)

    # Check if there are more comments to load
    has_more_comments = comments.has_next

    # Prepare data for response
    comment_data = [{
        'username': comment.user.username,
        'content': comment.content,
        'timestamp': comment.timestamp.strftime('%b %d, %Y %H:%M'),
        'avatar': comment.user.get_avatar()
    } for comment in comments.items]

    return jsonify({
        'comments': comment_data,
        'has_more_comments': has_more_comments
    })
