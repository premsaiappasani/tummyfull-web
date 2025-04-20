from flask import Blueprint, render_template, jsonify, session, request
from models.user import User
import datetime
from models.meal import Meal

meal_routes = Blueprint('meal_routes', __name__)

@meal_routes.route('/booking/meal', methods=['GET'])
def meal_booking():
    print("Welcome to the Booking")
    # Remove in production
    class DummyUser:
        def __init__(self, name, employeeId, email):
            self.name = name
            self.employeeId = employeeId
            self.email = email
            self._id = 'dummy_user_id_123'

    dummy_user = DummyUser(
        name='Test User',
        employeeId='EMP999',
        email='test.user@nielsen.com'
    )
    
    return render_template('book_meal.html', user=dummy_user)

@meal_routes.route('/booking/meal', methods=['POST'])
def redeem_meal():
    print("Redeeming the booking")
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"success": False, "message": "Unauthorized. Please log in."}), 401

    user = User.find_by_id(user_id)
    if not user:
        print(f"Error: User ID {user_id} in session not found in DB.")
        session.pop('user_id', None)
        return jsonify({"success": False, "message": "Invalid user session. Please log in again."}), 401

    data = request.get_json()
    if not data or 'qrData' not in data:
        return jsonify({"success": False, "message": "Missing QR data in request body"}), 400

    qr_data_scanned = data['qrData'].strip()
    
    expected_company = "nielsen"
    today_str = datetime.date.today().strftime('%Y-%m-%d')
    is_qr_date_correct = f"date={today_str}" in qr_data_scanned
    is_qr_company_correct = f"company={expected_company}" in qr_data_scanned

    if not is_qr_date_correct or not is_qr_company_correct:
        print(f"QR data validation failed for user {user_id}: {qr_data_scanned}")
        return jsonify({"success": False, "message": "Invalid QR code. Please scan today's vendor QR."}), 400

    if Meal.has_redeemed_today(user._id):
        print(f"User {user_id} already redeemed meal today.")
        return jsonify({"success": False, "message": "You have already redeemed your meal today."}), 409

    try:
        redemption_id = Meal.create_redemption_entry(user._id, qr_data_scanned)

        if redemption_id:
            return jsonify({
                "success": True,
                "message": "Meal redeemed successfully!",
                "bookingId": str(redemption_id)
            }), 200

        else:
             print(f"Error: Failed to create redemption entry for user {user_id}.")
             return jsonify({"success": False, "message": "Failed to record meal redemption."}), 500


    except Exception as e:
        print(f"Error during meal redemption for user {user_id}: {e}")
        return jsonify({"success": False, "message": "An error occurred during meal redemption."}), 500


def get_blueprint():
    return meal_routes