from flask import Blueprint
from models.user import User

main_routes = Blueprint('main_routes', __name__)

@main_routes.route('/')
def home():
    print("All Users:")
    users = User.find_all()
    for user in users:
        print(f"User ID: {user._id}, Username: {user.username}")
    return "Welcome to the Meal App!"

def get_blueprint():
    return main_routes