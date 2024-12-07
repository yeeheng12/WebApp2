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
app.config['UPLOAD_FOLDER'] = 'static/images/uploads'
app.config['DEFAULT_AVATAR_FOLDER'] = 'static/images/default'
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max file size (16MB)

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
            flash("Login successful!", "success")
            return redirect(url_for('home'))
        flash("Login unsuccessful. Check username and password.", "danger")
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

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
            avatar.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
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

        # Handle image upload for the post
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))  # Save the image
        else:
            filename = None  # No image uploaded

        # Create a new post
        new_post = Post(content=content, author=current_user, image=filename)
        new_post.set_tags()  # Extract and store hashtags
        db.session.add(new_post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))

    return render_template('create_post.html', form=form)

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

@app.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('q', '').strip()
    users = []
    posts = []
    form = SearchForm()

    if query:
        # Search for users by username (case-insensitive)
        users = User.query.filter(User.username.ilike(f'%{query}%')).all()

        # Search for posts by content or hashtags (case-insensitive)
        posts = Post.query.filter(
            (Post.content.ilike(f'%{query}%')) | 
            (Post.content.ilike(f'%#{query}%'))
        ).all()

    return render_template('search.html', query=query, users=users, posts=posts, form=form)

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

@app.route('/view_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()

    if form.validate_on_submit():
        comment = Comment(
            content=form.content.data,
            post_id=post.id,
            user_id=current_user.id
        )
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('view_post', post_id=post_id))

    return render_template('post.html', post=post, form=form)

