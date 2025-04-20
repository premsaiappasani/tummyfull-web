from flask import Flask
from db.connection import get_db
from controllers import register_blueprints
import os
import datetime

def create_app():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    views_path = os.path.join(project_root, 'views')
    app = Flask(__name__, template_folder=views_path)
    app.debug = True
    app.config.from_object('app.config.Config')
    app.permanent_session_lifetime = datetime.timedelta(hours=1)

    app.db = get_db()

    
    register_blueprints(app)

    return app