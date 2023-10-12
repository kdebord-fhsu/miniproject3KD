import sqlite3

import click
from flask import current_app, g


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def insert_student(username, password, role='student', full_name=None, student_id=None):
    db = get_db()
    db.execute(
        "INSERT INTO user (username, password, role, full_name, student_id) VALUES (?, ?, ?, ?, ?)",
        (username, generate_password_hash(password), role, full_name, student_id)
    )
    db.commit()

def get_student_by_username(username):
    db = get_db()
    return db.execute('SELECT * FROM user WHERE username = ?', (username,)).fetchone()

def get_student_by_id(student_id):
    db = get_db()
    return db.execute('SELECT * FROM user WHERE student_id = ?', (student_id,)).fetchone()

def update_student(student_id, full_name=None, password=None):
    db = get_db()
    if full_name:
        db.execute('UPDATE user SET full_name = ? WHERE id = ?', (full_name, student_id))
    if password:
        db.execute('UPDATE user SET password = ? WHERE id = ?', (generate_password_hash(password), student_id))
    db.commit()

def delete_student(student_id):
    db = get_db()
    db.execute('DELETE FROM user WHERE id = ?', (student_id,))
    db.commit()