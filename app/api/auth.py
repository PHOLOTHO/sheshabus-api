from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models.user import User, AdminUser
from app.services.email_service import EmailService
from app.utils.validators import validate_email, validate_password
import random
import string
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        print(f"🔍 [REGISTRATION START] Registration attempt with data: {data}")

        # Validation
        required_fields = ['email', 'password', 'first_name', 'last_name', 'phone']
        for field in required_fields:
            if not data.get(field):
                print(f"❌ [VALIDATION] Missing field: {field}")
                return jsonify({'message': f'{field} is required'}), 400

        if not validate_email(data['email']):
            print(f"❌ [VALIDATION] Invalid email: {data['email']}")
            return jsonify({'message': 'Invalid email format'}), 400

        if not validate_password(data['password']):
            print("❌ [VALIDATION] Password too short")
            return jsonify({'message': 'Password must be at least 8 characters long'}), 400

        # Check if user exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            print(f"❌ [VALIDATION] User already exists: {data['email']}")
            return jsonify({'message': 'User already exists'}), 400

        # Create user
        user = User(
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone=data['phone']
        )
        user.set_password(data['password'])

        # Generate verification token
        verification_token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        user.email_verification_token = verification_token

        print(f"🔍 [DB] About to add user to database: {user.email}")
        print(f"🔍 [USER DETAILS] First name: '{user.first_name}', Email: '{user.email}'")

        db.session.add(user)
        db.session.commit()

        print(f"✅ [DB] User committed to database with ID: {user.id}")

        # Send verification email - ADD COMPREHENSIVE DEBUGGING
        print(f"🔍 [EMAIL] Attempting to send email to: {user.email}")
        print(f"🔍 [EMAIL] First name for email: '{user.first_name}'")
        print(f"🔍 [EMAIL] Verification token: '{verification_token}'")
        print(f"🔍 [EMAIL] About to call EmailService.send_verification_email()")

        # Test the parameters before sending
        if not user.first_name or user.first_name.strip() == "":
            print("❌ [EMAIL] WARNING: first_name is empty!")
        if not user.email or user.email.strip() == "":
            print("❌ [EMAIL] WARNING: email is empty!")
        if not verification_token or verification_token.strip() == "":
            print("❌ [EMAIL] WARNING: verification_token is empty!")

        # Call the email service
        email_sent = EmailService.send_verification_email(user.email, user.first_name, verification_token)

        if email_sent:
            print("✅ [EMAIL] Email service returned SUCCESS")
        else:
            print("❌ [EMAIL] Email service returned FAILURE")

        print(f"✅ [REGISTRATION COMPLETE] User {user.email} registered successfully")

        return jsonify({
            'message': 'User registered successfully. Please check your email for verification.',
            'user': user.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"💥 [REGISTRATION ERROR] Exception: {str(e)}")
        import traceback
        print(f"💥 [TRACEBACK] {traceback.format_exc()}")
        return jsonify({'message': 'Registration failed', 'error': str(e)}), 500

@auth_bp.route('/verify-email', methods=['POST'])
def verify_email():
    try:
        data = request.get_json()
        token = data.get('token')

        if not token:
            return jsonify({'message': 'Verification token is required'}), 400

        user = User.query.filter_by(email_verification_token=token).first()
        if not user:
            return jsonify({'message': 'Invalid verification token'}), 400

        user.is_verified = True
        user.email_verification_token = None
        db.session.commit()

        return jsonify({'message': 'Email verified successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Verification failed', 'error': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'message': 'Email and password are required'}), 400

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return jsonify({'message': 'Invalid credentials'}), 401

        if not user.is_verified:
            return jsonify({'message': 'Please verify your email first'}), 401

        access_token = create_access_token(identity=str(user.id))

        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': user.to_dict()
        }), 200

    except Exception as e:
        return jsonify({'message': 'Login failed', 'error': str(e)}), 500


@auth_bp.route('/admin/login', methods=['POST'])
def admin_login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'message': 'Email and password are required'}), 400

        admin = AdminUser.query.filter_by(email=email, is_active=True).first()
        if not admin or not admin.check_password(password):
            return jsonify({'message': 'Invalid credentials'}), 401

        access_token = create_access_token(identity=f"admin_{admin.id}")

        return jsonify({
            'message': 'Admin login successful',
            'access_token': access_token,
            'admin': admin.to_dict()
        }), 200

    except Exception as e:
        return jsonify({'message': 'Login failed', 'error': str(e)}), 500


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    try:
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({'message': 'Email is required'}), 400

        user = User.query.filter_by(email=email).first()
        if user:
            # Generate reset token
            reset_token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
            user.reset_token = reset_token
            # Token expires in 1 hour
            user.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)

            db.session.commit()

            # Send reset email
            EmailService.send_password_reset_email(user.email, user.first_name, reset_token)

        return jsonify({'message': 'If the email exists, a password reset link has been sent'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Password reset request failed', 'error': str(e)}), 500


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    try:
        data = request.get_json()
        token = data.get('token')
        new_password = data.get('new_password')

        if not token or not new_password:
            return jsonify({'message': 'Token and new password are required'}), 400

        if not validate_password(new_password):
            return jsonify({'message': 'Password must be at least 8 characters long'}), 400

        user = User.query.filter_by(reset_token=token).first()
        if not user or user.reset_token_expiry < datetime.utcnow():
            return jsonify({'message': 'Invalid or expired reset token'}), 400

        user.set_password(new_password)
        user.reset_token = None
        user.reset_token_expiry = None
        db.session.commit()

        return jsonify({'message': 'Password reset successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Password reset failed', 'error': str(e)}), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required()
def refresh_token():
    try:
        current_user_id = get_jwt_identity()

        if current_user_id.startswith('admin_'):
            admin_id = int(current_user_id.replace('admin_', ''))
            admin = AdminUser.query.get(admin_id)
            if not admin:
                return jsonify({'message': 'Admin not found'}), 404

            new_token = create_access_token(identity=current_user_id)
            return jsonify({
                'access_token': new_token,
                'admin': admin.to_dict()
            }), 200
        else:
            user = User.query.get(int(current_user_id))
            if not user:
                return jsonify({'message': 'User not found'}), 404

            new_token = create_access_token(identity=current_user_id)
            return jsonify({
                'access_token': new_token,
                'user': user.to_dict()
            }), 200

    except Exception as e:
        return jsonify({'message': 'Token refresh failed', 'error': str(e)}), 500


@auth_bp.route('/resend-verification', methods=['POST'])
def resend_verification():
    data = request.get_json()
    email = data.get('email')

    user = User.query.filter_by(email=email, is_verified=False).first()
    if not user:
        return jsonify({'message': 'If an unverified account exists, a new code has been sent'}), 200

    # ✅ Use same token format as registration
    import string
    new_token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    user.email_verification_token = new_token
    db.session.commit()

    EmailService.send_verification_email(user.email, user.first_name, new_token)

    return jsonify({'message': 'Verification code sent'}), 200