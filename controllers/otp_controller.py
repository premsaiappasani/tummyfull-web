from flask import Blueprint, request, jsonify, session, render_template
import random
import datetime
import smtplib
from email.mime.text import MIMEText
import os
from models.otp import OTP
from models.user import User
from flask import current_app


otp_routes = Blueprint('otp_routes', __name__)


SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'your_email@example.com')
SENDER_PASSWORD = os.environ.get('SENDER_PASSWORD', 'your_email_password')


def send_email(recipient_email, otp_code):
    subject = "Your Meal App OTP"
    body = f"Your One-Time Password (OTP) is: {otp_code}\n\nThis OTP is valid for 5 minutes."

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = recipient_email

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())
        print(f"OTP email sent successfully to {recipient_email}")
        return True
    except Exception as e:
        print(f"Failed to send OTP email to {recipient_email}: {e}")
        return False


@otp_routes.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json()

    if not data or 'email' not in data or 'employeeId' not in data:
        return jsonify({"message": "Missing email or employee ID in request body"}), 400

    email = data['email'].strip()
    empId = data['employeeId'].strip()


    otp_code = str(random.randint(100000, 999999))

    try:
        otps_collection = OTP.get_collection()
        otps_collection.delete_many({'email': email, 'is_used': False, 'expiry_time': {'$gt': datetime.datetime.now()}})

        OTP.create_and_save(email, otp_code, expiry_minutes=5)
        print(f"OTP stored in DB for {email} using model")
    except Exception as e:
        print(f"Failed to store OTP in DB for {email} using model: {e}")
        return jsonify({"success": False, "message": "Failed to store OTP"}), 500


    email_sent_success = send_email(email, otp_code)

    if email_sent_success:
        return jsonify({"success": True, "message": "OTP sent to your email"}), 200
    else:
        return jsonify({"success": False, "message": "Failed to send OTP email"}), 500


@otp_routes.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()

    if not data or 'email' not in data or 'otp' not in data:
        return jsonify({"message": "Missing email or OTP in request body"}), 400

    email = data['email'].strip()
    entered_otp = data['otp'].strip()
    empId = data.get('employeeId', '').strip()


    otp_object = OTP.find_active_by_email(email)


    if otp_object:
        stored_otp = otp_object.otp_code

        if entered_otp == stored_otp:

            try:
                otp_object.mark_as_used()
                print(f"OTP {otp_object._id} marked as used for {email} using model")
            except Exception as e:
                print(f"Failed to mark OTP {otp_object._id} as used for {email} using model: {e}")
                return jsonify({"success": False, "message": "OTP verified but failed to update status. Please contact support."}), 500


            user = User.find_by_email_and_employeeId(email, empId)

            if user:
                session['user_id'] = str(user._id)

                session.permanent = True

                print(f"User {user._id} authenticated and session set.")

                return render_template('book_meal.html', user=user)


            else:
                print(f"Error: User not found in DB after successful OTP verification for email: {email}")
                session.pop('user_id', None)
                return jsonify({"success": False, "message": "User not found after verification. Please contact support."}), 500


        else:
            return jsonify({"success": False, "message": "Invalid OTP"}), 400

    else:
        return jsonify({"success": False, "message": "No valid OTP found for this email. Please request a new one."}), 400
