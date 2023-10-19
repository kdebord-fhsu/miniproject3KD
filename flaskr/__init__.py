# INF - 601
# Kelton DeBord
# Mini Project 3
import os
from flask import Flask, render_template
from . import db
from .auth import bp as auth_bp
from .blog import bp as blog_bp

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize the database
    db.init_app(app)

    # Define the index route
    @app.route('/')
    def index():
        return render_template('/auth/login.html')  # You can render a template or any other response here

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(blog_bp, url_prefix='/blog')

    return app
