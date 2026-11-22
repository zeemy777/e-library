
from pathlib import Path

from flask import (
    Blueprint,
    jsonify,
    request,
    send_file,
    session
)

from sqlalchemy import func, or_

from config import Config
from extensions import db
from models import Category, Resource, Review

library_bp = Blueprint(
    "library",
    __name__,
    url_prefix="/api"
)


# =====================================
# DOWNLOAD PERMISSION HELPERS
# =====================================

# A resource can be downloaded when its own override is set,
# otherwise it inherits the permission of its category.
def can_download(resource):

    if resource.download_override is not None:
        return bool(resource.download_override)

    return bool(resource.category.allow_download)


# Resolve the stored file path inside the uploads folder.
# This also blocks path-traversal attempts such as "../../file".
def resolve_file(resource):

    if not resource.file_path:
        return None

    upload_root = Path(Config.UPLOAD_FOLDER).resolve()
    file_path = (upload_root / resource.file_path).resolve()

    if upload_root not in file_path.parents:
        return None

    if not file_path.is_file():
        return None

    return file_path


# Shared serializer so every endpoint exposes the same fields.
def resource_response(resource):

    file_path = resolve_file(resource)

    rating_row = db.session.query(
        func.avg(Review.rating),
        func.count(Review.id)
    ).filter(
        Review.resource_id == resource.id
    ).first()

    average_rating = (
        round(rating_row[0], 1) if rating_row[0] else None
    )

    return {
        "id": resource.id,
        "title": resource.title,
        "resource_type": resource.resource_type,
        "author": resource.author,
        "publisher": resource.publisher,
        "description": resource.description,
        "category_id": resource.category_id,
        "category": resource.category.name,
        "cover_image": resource.cover_image,
        "video_url": resource.video_url,
        "is_published": resource.is_published,
        "can_download": can_download(resource),
        "has_file": file_path is not None,
        "readable": (
            file_path is not None
            and file_path.suffix.lower() == ".pdf"
        ),
        "average_rating": average_rating,
        "rating_count": rating_row[1] or 0,
        "created_at": (
            resource.created_at.isoformat()
            if resource.created_at else None
        )
    }


# =====================================
# SERVE UPLOADED MEDIA
# Covers and videos stored in backend/uploads.
# =====================================

@library_bp.route("/media/<path:relative_path>", methods=["GET"])
def media_file(relative_path):

    upload_root = Path(Config.UPLOAD_FOLDER).resolve()
    file_path = (upload_root / relative_path).resolve()

    if upload_root not in file_path.parents:
        return jsonify({
            "status": "error",
            "message": "File not found."
        }), 404

    if not file_path.is_file():
        return jsonify({
            "status": "error",
            "message": "File not found."
        }), 404

    # conditional=True supports range requests for video seeking.
    # Do not wrap this in a status tuple: it would override the 206.
    return send_file(file_path, conditional=True)


# =====================================
# GET ALL CATEGORIES
# =====================================

@library_bp.route("/categories", methods=["GET"])
def get_categories():

    categories = Category.query.order_by(Category.name).all()

    return jsonify({
        "status": "success",
        "categories": [
            {
                "id": category.id,
                "name": category.name,
                "description": category.description,
                "allow_download": category.allow_download
            }
            for category in categories
        ]
    }), 200


# =====================================
# PUBLIC LIBRARY STATISTICS
# =====================================

@library_bp.route("/stats", methods=["GET"])
def get_stats():

    published = Resource.query.filter_by(is_published=True)

    return jsonify({
        "status": "success",
        "stats": {
            "resources": published.count(),
            "books": published.filter_by(
                resource_type="book"
            ).count(),
            "videos": published.filter_by(
                resource_type="video"
            ).count(),
            "categories": Category.query.count()
        }
    }), 200


# =====================================
# GET ALL PUBLISHED RESOURCES
# =====================================

@library_bp.route("/resources", methods=["GET"])
def get_resources():

    query = Resource.query.filter_by(is_published=True)

    # Optional category filter.
    category_id = request.args.get("category_id", type=int)

    if category_id is not None:
        query = query.filter_by(category_id=category_id)

    # Optional resource type filter (book or video).
    resource_type = request.args.get(
        "resource_type", ""
    ).strip().lower()

    if resource_type in ("book", "video"):
        query = query.filter_by(resource_type=resource_type)

    # Optional search across title, author and publisher.
    search = request.args.get("search", "").strip()

    if search:
        pattern = f"%{search}%"

        query = query.filter(
            or_(
                Resource.title.ilike(pattern),
                Resource.author.ilike(pattern),
                Resource.publisher.ilike(pattern)
            )
        )

    query = query.order_by(
        Resource.created_at.desc(),
        Resource.id.desc()
    )

    total = query.count()

    # Optional paging so the catalogue can load in batches.
    limit = request.args.get("limit", type=int)
    offset = max(request.args.get("offset", 0, type=int) or 0, 0)

    if limit is not None:
        limit = min(max(limit, 1), 200)
        resources = query.offset(offset).limit(limit).all()
    else:
        resources = query.offset(offset).all()

    return jsonify({
        "status": "success",
        "total": total,
        "offset": offset,
        "has_more": offset + len(resources) < total,
        "resources": [
            resource_response(resource)
            for resource in resources
        ]
    }), 200


# =====================================
# GET ONE RESOURCE
# =====================================

@library_bp.route("/resources/<int:resource_id>", methods=["GET"])
def get_resource(resource_id):

    resource = Resource.query.filter_by(
        id=resource_id,
        is_published=True
    ).first()

    if not resource:
        return jsonify({
            "status": "error",
            "message": "Resource not found."
        }), 404

    return jsonify({
        "status": "success",
        "resource": resource_response(resource)
    }), 200


# =====================================
# DOWNLOAD A BOOK
# =====================================

@library_bp.route(
    "/resources/<int:resource_id>/download",
    methods=["GET"]
)
def download_resource(resource_id):

    # Downloading is reserved for logged-in members.
    if not session.get("user_id"):
        return jsonify({
            "status": "error",
            "message": "Please log in to download this book."
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

    # Only book resources can be downloaded.
    if resource.resource_type != "book":
        return jsonify({
            "status": "error",
            "message": "Only books can be downloaded."
        }), 400

    # Apply the category or per-book download permission.
    if not can_download(resource):
        return jsonify({
            "status": "error",
            "message": "Download is not permitted for this book."
        }), 403

    file_path = resolve_file(resource)

    if not file_path:
        return jsonify({
            "status": "error",
            "message": "The book file is not available."
        }), 404

    return send_file(
        file_path,
        as_attachment=True,
        download_name=f"{resource.title}{file_path.suffix}"
    ), 200


# =====================================
# READ A BOOK ONLINE
# =====================================

@library_bp.route(
    "/resources/<int:resource_id>/read",
    methods=["GET"]
)
def read_resource(resource_id):

    # Online reading is available to registered users.
    if not session.get("user_id"):
        return jsonify({
            "status": "error",
            "message": "Please log in to read this book."
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

    if resource.resource_type != "book":
        return jsonify({
            "status": "error",
            "message": "Only books can be read online."
        }), 400

    file_path = resolve_file(resource)

    if not file_path:
        return jsonify({
            "status": "error",
            "message": "The book file is not available."
        }), 404

    # Browsers can display PDF files inline.
    if file_path.suffix.lower() != ".pdf":
        return jsonify({
            "status": "error",
            "message": "Only PDF books can be read online."
        }), 400

    return send_file(
        file_path,
        mimetype="application/pdf",
        as_attachment=False
    ), 200
