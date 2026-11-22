
# Import Flask tools for creating the contact endpoint.
from flask import Blueprint, jsonify, request

# Import the database extension and contact model.
from extensions import db
from models import ContactMessage


# Create the contact blueprint.
contact_bp = Blueprint(
    "contact",
    __name__,
    url_prefix="/api"
)


# =====================================
# SUBMIT A CONTACT MESSAGE
# =====================================

@contact_bp.route("/contact", methods=["POST"])
def create_contact_message():

    # Receive the inquiry from React.
    data = request.get_json(silent=True) or {}

    full_name = str(data.get("full_name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    subject = str(data.get("subject", "")).strip()
    message = str(data.get("message", "")).strip()

    # Validate required fields.
    if not full_name or not email or not subject or not message:
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

    # Keep the stored message to a reasonable size.
    if len(message) > 5000:
        return jsonify({
            "status": "error",
            "message": "Message must be 5000 characters or fewer."
        }), 400

    # Store the inquiry for the admin to review.
    new_message = ContactMessage(
        full_name=full_name,
        email=email,
        subject=subject,
        message=message
    )

    db.session.add(new_message)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": (
            "Thank you! Your inquiry has been received. "
            "The library team will get back to you soon."
        )
    }), 201
