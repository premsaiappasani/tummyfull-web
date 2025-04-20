from flask import Blueprint, render_template
from models.user import User

main_routes = Blueprint('main_routes', __name__)

@main_routes.route('/')
def home():
    print("Welcome to the Meal App!")
    return render_template('home.html')

def get_blueprint():
    return main_routes