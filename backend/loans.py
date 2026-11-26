
from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request, session

from extensions import db
from library import resource_response
from models import Loan, Resource, User

loans_bp = Blueprint(
    "loans",
    __name__,
    url_prefix="/api/loans"
)

# Members keep a borrowed book for two weeks.
LOAN_PERIOD_DAYS = 14

# Maximum books a member can have out at once.
MAX_ACTIVE_LOANS = 5


# Return the signed-in member, or None for guests.
def get_member():

    user_id = session.get("user_id")

    if not user_id:
        return None

    user = db.session.get(User, user_id)

    if not user or not user.is_active:
        return None

    return user


# Shared loan serializer.
def loan_response(loan):

    status = "returned"

    if loan.returned_at is None:
        if loan.is_overdue:
            status = "overdue"
        else:
            status = "active"

    return {
        "id": loan.id,
        "resource": resource_response(loan.resource),
        "borrowed_at": (
            loan.borrowed_at.isoformat()
            if loan.borrowed_at else None
        ),
        "due_date": (
            loan.due_date.isoformat()
            if loan.due_date else None
        ),
        "returned_at": (
            loan.returned_at.isoformat()
            if loan.returned_at else None
        ),
        "status": status
    }


# =====================================
# LIST MY LOANS
# =====================================

@loans_bp.route("/mine", methods=["GET"])
def my_loans():

    user = get_member()

    if not user:
        return jsonify({
            "status": "error",
            "message": "Please log in to view your loans."
        }), 401

    loans = Loan.query.filter_by(
        user_id=user.id
    ).order_by(Loan.borrowed_at.desc()).all()

    active = []
    history = []

    for loan in loans:
        if loan.returned_at is None:
            active.append(loan_response(loan))
        else:
            history.append(loan_response(loan))

    return jsonify({
        "status": "success",
        "active": active,
        "history": history
    }), 200


# =====================================
# BORROW A BOOK
# =====================================

@loans_bp.route("", methods=["POST"])
def borrow_book():

    user = get_member()

    if not user:
        return jsonify({
            "status": "error",
            "message": "Please log in to borrow books."
        }), 401

    data = request.get_json(silent=True) or {}

    resource_id = data.get("resource_id")

    resource = Resource.query.filter_by(
        id=resource_id,
        is_published=True
    ).first()

    if not resource:
        return jsonify({
            "status": "error",
            "message": "Book not found."
        }), 404

    # Only local books can be borrowed. Streamed books are read at their
    # source and have no file to return.
    if resource.resource_type != "book":
        return jsonify({
            "status": "error",
            "message": "Only books can be borrowed."
        }), 400

    if resource.external_url:
        return jsonify({
            "status": "error",
            "message": "This book is read online and cannot be borrowed."
        }), 400

    # The member must not already have this book out.
    existing = Loan.query.filter_by(
        user_id=user.id,
        resource_id=resource.id,
        returned_at=None
    ).first()

    if existing:
        return jsonify({
            "status": "error",
            "message": f'You already have "{resource.title}" on loan.'
        }), 409

    active_count = Loan.query.filter_by(
        user_id=user.id,
        returned_at=None
    ).count()

    if active_count >= MAX_ACTIVE_LOANS:
        return jsonify({
            "status": "error",
            "message": (
                f"You can only borrow up to {MAX_ACTIVE_LOANS} "
                "books at a time."
            )
        }), 409

    loan = Loan(
        user_id=user.id,
        resource_id=resource.id,
        due_date=datetime.utcnow() + timedelta(days=LOAN_PERIOD_DAYS)
    )

    db.session.add(loan)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": (
            f'You borrowed "{resource.title}". '
            f"Please return it within {LOAN_PERIOD_DAYS} days."
        ),
        "loan": loan_response(loan)
    }), 201


# =====================================
# RETURN A BOOK
# =====================================

@loans_bp.route("/<int:loan_id>/return", methods=["POST"])
def return_book(loan_id):

    user = get_member()

    if not user:
        return jsonify({
            "status": "error",
            "message": "Please log in to return books."
        }), 401

    loan = Loan.query.filter_by(
        id=loan_id,
        user_id=user.id
    ).first()

    if not loan:
        return jsonify({
            "status": "error",
            "message": "Loan not found."
        }), 404

    if loan.returned_at is not None:
        return jsonify({
            "status": "error",
            "message": "This book has already been returned."
        }), 409

    loan.returned_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": (
            f'"{loan.resource.title}" was returned. Thank you!'
        ),
        "loan": loan_response(loan)
    }), 200
