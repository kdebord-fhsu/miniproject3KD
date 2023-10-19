from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db

# Create a Blueprint instance for the blog routes
bp = Blueprint('blog', __name__, url_prefix='/blog')

# Index route - displays all posts
@bp.route('/')
def index():
    db = get_db()
    # Fetch posts from the database and pass them to the template
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)

# Create route - allows authenticated users to create new posts
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            # Insert the new post into the database
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

# Helper function to retrieve a post by its ID
def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

# Update route - allows users to edit their own posts
@bp.route('/update/<int:id>', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            # Update the post in the database
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)

# Delete route - allows users to delete their own posts
@bp.route('/delete/<int:id>', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    # Delete the post from the database
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))

# My Posts route - displays posts created by the logged-in user
@bp.route('/my-posts')
@login_required(role='student')  # Example usage of login_required with role check
def my_posts():
    db = get_db()
    # Fetch posts created by the user from the database
    posts = db.execute(
        'SELECT id, title, body, created FROM post WHERE author_id = ? ORDER BY created DESC',
        (g.user['id'],)
    ).fetchall()
    return render_template('blog/my_posts.html', posts=posts)
