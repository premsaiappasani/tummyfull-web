from flask import Flask
from db.connection import get_db

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    app.db = get_db()

    from controllers import register_blueprints
    register_blueprints(app)

    return app