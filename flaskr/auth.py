from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from flask import g, redirect, url_for
from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        role = role if role in ['student', 'teacher', 'admin'] else 'student'
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password, role) VALUES (?, ?, ?)",
                    (username, generate_password_hash(password), role),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM student WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['full_name'] = user['full_name']
            session['student_id'] = user['student_id']
            return redirect(url_for('index'))  # Redirect to the home page or student dashboard

        flash(error)

    return render_template('auth/login.html')
@bp.route('/profile')
@login_required
def login_required(role=None):
    def decorator(view):
        @wraps(view)
        def wrapped_view(*args, **kwargs):
            if g.user is None:
                return redirect(url_for('auth.login'))

            if role and g.user['role'] != role:
                # Redirect to an unauthorized page or show an error message
                return "Unauthorized Access", 403  # HTTP status code for forbidden access

            return view(*args, **kwargs)
        return wrapped_view
    return decorator


