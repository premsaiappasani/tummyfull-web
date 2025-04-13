from flask import Blueprint
from .controllers import register_blueprints

main_routes = Blueprint('main_routes', __name__)

@main_routes.route('/')
def home():
    return "Welcome to the Meal App!"

def init_app(app):
    app.register_blueprint(main_routes)
    register_blueprints(app)