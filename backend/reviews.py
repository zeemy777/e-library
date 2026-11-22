
from flask import Blueprint, jsonify, request, session

from extensions import db
from models import Resource, Review, User

reviews_bp = Blueprint(
    "reviews",
    __name__,
    url_prefix="/api/resources"
)


# Return the signed-in member, or None for guests.
def get_member():

    user_id = session.get("user_id")

    if not user_id:
        return None

    user = db.session.get(User, user_id)

    if not user or not user.is_active:
        return None

    return user


# Shared review serializer.
def review_response(review, viewer=None):

    mine = bool(viewer) and viewer.id == review.user_id

    return {
        "id": review.id,
        "rating": review.rating,
        "comment": review.comment,
        "reviewer": review.user.full_name if review.user else "Member",
        "mine": mine,
        "created_at": (
            review.created_at.isoformat()
            if review.created_at else None
        )
    }


# =====================================
# LIST REVIEWS FOR A RESOURCE
# =====================================

@reviews_bp.route("/<int:resource_id>/reviews", methods=["GET"])
def list_reviews(resource_id):

    resource = Resource.query.filter_by(
        id=resource_id,
        is_published=True
    ).first()

    if not resource:
        return jsonify({
            "status": "error",
            "message": "Resource not found."
        }), 404

    reviews = Review.query.filter_by(
        resource_id=resource.id
    ).order_by(Review.created_at.desc()).all()

    viewer = get_member()

    return jsonify({
        "status": "success",
        "reviews": [
            review_response(review, viewer)
            for review in reviews
        ]
    }), 200


# =====================================
# SUBMIT OR UPDATE MY REVIEW
# =====================================

@reviews_bp.route("/<int:resource_id>/reviews", methods=["POST"])
def submit_review(resource_id):

    user = get_member()

    if not user:
        return jsonify({
            "status": "error",
            "message": "Please log in to write a review."
        }), 401

    resource = Resource.query.filter_by(
        id=resource_id,
        is_published=True
    ).first()

    if not resource:
        return jsonify({
            "status": "error",
            "message": "Resource not found."
        }), 404

    data = request.get_json(silent=True) or {}

    try:
        rating = int(data.get("rating"))
    except (TypeError, ValueError):
        rating = 0

    comment = str(data.get("comment", "")).strip()

    if rating < 1 or rating > 5:
        return jsonify({
            "status": "error",
            "message": "Rating must be between 1 and 5 stars."
        }), 400

    if len(comment) > 1000:
        return jsonify({
            "status": "error",
            "message": "Review must be 1000 characters or fewer."
        }), 400

    # Members may edit their earlier review instead of
    # stacking duplicates of the same resource.
    review = Review.query.filter_by(
        user_id=user.id,
        resource_id=resource.id
    ).first()

    if not review:
        review = Review(
            user_id=user.id,
            resource_id=resource.id
        )
        db.session.add(review)

    review.rating = rating
    review.comment = comment or None
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Thanks! Your review was saved.",
        "review": review_response(review, user)
    }), 200


# =====================================
# DELETE MY REVIEW
# =====================================

@reviews_bp.route("/<int:resource_id>/reviews/mine", methods=["DELETE"])
def delete_review(resource_id):

    user = get_member()

    if not user:
        return jsonify({
            "status": "error",
            "message": "Please log in to manage your reviews."
        }), 401

    review = Review.query.filter_by(
        user_id=user.id,
        resource_id=resource_id
    ).first()

    if not review:
        return jsonify({
            "status": "error",
            "message": "Review not found."
        }), 404

    db.session.delete(review)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Your review was removed."
    }), 200
