from flask import Blueprint, request, jsonify
from models.user import User

user_routes = Blueprint('user_routes', __name__)

@user_routes.route('/users')
def get_users():
    users = User.find_all()
    for user in users:
        print(f"User ID: {user._id}, Username: {user.username}")
    return "List of users"

@user_routes.route('/user', methods=['GET'])
def find_user():
    email = request.args.get('email')
    employeeId = request.args.get('employeeId')
    if not email or not employeeId:
        return jsonify({"message": "Missing email or employee ID query parameters"}), 400
    
    user = User.find_by_email_and_employeeId(email, employeeId)

    if user:
        return jsonify({"exists": True, "userId": str(user._id)}), 200
    else:
        return jsonify({"exists": False}), 200
    
@user_routes.route('/user', methods=['POST'])
def register_user():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Request body must be JSON"}), 415
    
    required_fields = ['email', 'employeeId', 'name']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"message": f"Missing or empty required field: {field}"}), 400
    
    email = data['email'].strip()
    employeeId = data['employeeId'].strip()
    name = data['name'].strip()

    existing_user = User.find_by_email_and_employeeId(email, employeeId)
    if existing_user:
        return jsonify({"message": "User with this email and employee ID already exists"}), 409
    
    try:
        new_user = User(
            name=name,
            employeeId=employeeId,
            email=email,
            is_admin=data.get('is_admin', False),
            is_active=data.get('is_active', True),
            is_vendor=data.get('is_vendor', False)
        )
        new_user.save()
        return jsonify({
            "message": "User registered successfully",
            "userId": str(new_user._id)
        }), 201
    except Exception as e:
        print(f"Error during user registration: {e}")
        return jsonify({"message": "An error occurred during user registration"}), 500

def get_blueprint():
    return user_routes