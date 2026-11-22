
from flask import Blueprint, jsonify, session

from extensions import db
from library import resource_response
from models import Favorite, Resource, User

favorites_bp = Blueprint(
    "favorites",
    __name__,
    url_prefix="/api/favorites"
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


# =====================================
# LIST THE MEMBER'S SHELF
# =====================================

@favorites_bp.route("", methods=["GET"])
def list_favorites():

    user = get_member()

    if not user:
        return jsonify({
            "status": "error",
            "message": "Please log in to view your shelf."
        }), 401

    favorites = Favorite.query.filter_by(
        user_id=user.id
    ).order_by(Favorite.created_at.desc()).all()

    resources = [
        favorite.resource
        for favorite in favorites
        if favorite.resource and favorite.resource.is_published
    ]

    return jsonify({
        "status": "success",
        "favorites": [
            resource_response(resource)
            for resource in resources
        ]
    }), 200


# =====================================
# SAVE A RESOURCE TO THE SHELF
# =====================================

@favorites_bp.route("/<int:resource_id>", methods=["POST"])
def add_favorite(resource_id):

    user = get_member()

    if not user:
        return jsonify({
            "status": "error",
            "message": "Please log in to save this resource."
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

    existing = Favorite.query.filter_by(
        user_id=user.id,
        resource_id=resource.id
    ).first()

    if not existing:
        db.session.add(Favorite(
            user_id=user.id,
            resource_id=resource.id
        ))
        db.session.commit()

    return jsonify({
        "status": "success",
        "message": f'"{resource.title}" was added to your shelf.',
        "resource_id": resource.id
    }), 200


# =====================================
# REMOVE A RESOURCE FROM THE SHELF
# =====================================

@favorites_bp.route("/<int:resource_id>", methods=["DELETE"])
def remove_favorite(resource_id):

    user = get_member()

    if not user:
        return jsonify({
            "status": "error",
            "message": "Please log in to update your shelf."
        }), 401

    favorite = Favorite.query.filter_by(
        user_id=user.id,
        resource_id=resource_id
    ).first()

    if favorite:
        db.session.delete(favorite)
        db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Removed from your shelf.",
        "resource_id": resource_id
    }), 200
