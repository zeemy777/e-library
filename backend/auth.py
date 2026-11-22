
# Import Flask tools for creating API endpoints.
from flask import Blueprint, request, jsonify, session

# Import password security functions.
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

# Import database extension and User model.
from extensions import db
from models import User

# Import database integrity error handling.
from sqlalchemy.exc import IntegrityError


# Create authentication blueprint.
auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/api/auth"
)


# Helper function for returning safe user information.
# Never return the user's password hash.
def user_response(user):

    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "role": user.role
    }


# Return the logged-in, active user or None.
def get_logged_in_user():

    user_id = session.get("user_id")

    if not user_id:
        return None

    user = db.session.get(User, user_id)

    if not user or not user.is_active:
        return None

    return user


# =====================================
# USER REGISTRATION
# =====================================

@auth_bp.route("/register", methods=["POST"])
def register():

    # Receive registration information from React.
    data = request.get_json(silent=True) or {}

    full_name = str(data.get("full_name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = data.get("password", "")

    # Validate required information.
    if not full_name or not email or not password:
        return jsonify({
            "status": "error",
            "message": "All fields are required."
        }), 400

    # Basic email validation.
    if "@" not in email or "." not in email.split("@")[-1]:
        return jsonify({
            "status": "error",
            "message": "Enter a valid email address."
        }), 400

    # Validate password length.
    if len(password) < 8 or len(password) > 128:
        return jsonify({
            "status": "error",
            "message": "Password must be between 8 and 128 characters."
        }), 400

    # Check whether this email already exists.
    existing_user = User.query.filter_by(
        email=email
    ).first()

    if existing_user:
        return jsonify({
            "status": "error",
            "message": "An account with this email already exists."
        }), 409

    # Create a new member account.
    new_user = User(
        full_name=full_name,
        email=email,
        password_hash=generate_password_hash(password),
        role="member"
    )

    try:
        # Save the new account to MySQL.
        db.session.add(new_user)
        db.session.commit()

    except IntegrityError:
        db.session.rollback()

        return jsonify({
            "status": "error",
            "message": "This email address is already registered."
        }), 409

    # Return successful registration response.
    return jsonify({
        "status": "success",
        "message": "Account created successfully!",
        "user": user_response(new_user)
    }), 201


# =====================================
# USER LOGIN
# =====================================

@auth_bp.route("/login", methods=["POST"])
def login():

    # Receive login details.
    data = request.get_json(silent=True) or {}

    email = str(data.get("email", "")).strip().lower()
    password = data.get("password", "")

    # Check required fields.
    if not email or not password:
        return jsonify({
            "status": "error",
            "message": "Email and password are required."
        }), 400

    # Find the user in the database.
    user = User.query.filter_by(
        email=email
    ).first()

    # Check account and password.
    if (
        not user
        or not check_password_hash(user.password_hash, password)
        or not user.is_active
    ):
        return jsonify({
            "status": "error",
            "message": "Invalid email or password."
        }), 401

    # Clear previous session information.
    session.clear()

    # Store authenticated user ID in the session.
    session["user_id"] = user.id

    # Return user information.
    return jsonify({
        "status": "success",
        "message": "Login successful!",
        "user": user_response(user)
    })


# =====================================
# CURRENT USER
# =====================================

@auth_bp.route("/me", methods=["GET"])
def current_user():

    # Get the logged-in user's ID.
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({
            "status": "error",
            "message": "You are not logged in."
        }), 401

    # Retrieve the account from MySQL.
    user = db.session.get(User, user_id)

    if not user or not user.is_active:
        session.clear()

        return jsonify({
            "status": "error",
            "message": "Your session is no longer valid."
        }), 401

    return jsonify({
        "status": "success",
        "user": user_response(user)
    })


# =====================================
# USER LOGOUT
# =====================================

@auth_bp.route("/logout", methods=["POST"])
def logout():

    # Clear the user's session.
    session.clear()

    return jsonify({
        "status": "success",
        "message": "Logout successful!"
    })


# =====================================
# CHANGE PASSWORD
# =====================================

@auth_bp.route("/change-password", methods=["POST"])
def change_password():

    # Only logged-in, active users can change a password.
    user = get_logged_in_user()

    if not user:
        return jsonify({
            "status": "error",
            "message": "Please log in to change your password."
        }), 401

    data = request.get_json(silent=True) or {}

    current_password = data.get("current_password", "")
    new_password = data.get("new_password", "")

    # Check required fields.
    if not current_password or not new_password:
        return jsonify({
            "status": "error",
            "message": "Current and new passwords are required."
        }), 400

    # Verify the current password.
    if not check_password_hash(
        user.password_hash,
        current_password
    ):
        return jsonify({
            "status": "error",
            "message": "Current password is incorrect."
        }), 400

    # Validate the new password.
    if len(new_password) < 8 or len(new_password) > 128:
        return jsonify({
            "status": "error",
            "message": "Password must be between 8 and 128 characters."
        }), 400

    if current_password == new_password:
        return jsonify({
            "status": "error",
            "message": "New password must be different from the current one."
        }), 400

    # Save the new password hash.
    user.password_hash = generate_password_hash(new_password)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Password changed successfully!"
    }), 200
