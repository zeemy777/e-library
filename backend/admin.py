
# Import system helpers for file uploads.
import uuid
from datetime import datetime
from functools import wraps
from pathlib import Path

# Import Flask request tools.
from flask import Blueprint, jsonify, request

# Import password hashing and safe file names.
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

# Import database tools.
from extensions import db
from sqlalchemy import or_

# Import application models and helpers.
from auth import get_logged_in_user, user_response
from config import Config
from library import can_download, resolve_file, resource_response
from loans import loan_response
from models import (
    BookType,
    Category,
    ContactMessage,
    Loan,
    Resource,
    User
)


# Create the admin blueprint.
admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/api/admin"
)


# =====================================
# ADMIN ACCESS GUARD
# =====================================

def admin_required(view):

    @wraps(view)
    def wrapper(*args, **kwargs):

        user = get_logged_in_user()

        if not user:
            return jsonify({
                "status": "error",
                "message": "Please log in to continue."
            }), 401

        if user.role != "admin":
            return jsonify({
                "status": "error",
                "message": "Administrator access is required."
            }), 403

        return view(*args, **kwargs)

    return wrapper


# =====================================
# UPLOAD HELPERS
# =====================================

BOOK_EXTENSIONS = {"pdf", "epub"}
IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}


# Check the uploaded file extension.
def has_allowed_extension(filename, allowed):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in allowed
    )


# Store an uploaded file and return its database path.
def save_upload(file_storage, folder, allowed):

    filename = secure_filename(file_storage.filename or "")

    if not filename or not has_allowed_extension(filename, allowed):
        return None, "Unsupported file type."

    extension = filename.rsplit(".", 1)[1].lower()

    target_folder = Path(Config.UPLOAD_FOLDER) / folder
    target_folder.mkdir(parents=True, exist_ok=True)

    unique_name = f"{uuid.uuid4().hex}.{extension}"
    file_storage.save(target_folder / unique_name)

    return f"{folder}/{unique_name}", None


# Remove an uploaded file if it exists inside the uploads folder.
def delete_upload(relative_path):

    if not relative_path:
        return

    upload_root = Path(Config.UPLOAD_FOLDER).resolve()
    file_path = (upload_root / relative_path).resolve()

    if upload_root in file_path.parents and file_path.is_file():
        file_path.unlink()


# Convert form values into a boolean.
def parse_bool(value, default=False):

    if value is None:
        return default

    if isinstance(value, bool):
        return value

    return str(value).strip().lower() in {
        "1", "true", "yes", "on"
    }


# Convert the download override form value.
# "inherit" means use the category permission.
def parse_override(value):

    text = str(value or "").strip().lower()

    if text in ("", "inherit"):
        return None

    if text in ("allow", "true", "1", "yes"):
        return True

    if text in ("deny", "false", "0", "no"):
        return False

    return None


# Normalize a book type name before saving it.
def normalize_type_name(value):

    return " ".join(str(value).strip().lower().split())


# Add admin-only fields to the public resource serializer.
def admin_resource_response(resource):

    data = resource_response(resource)
    data["download_override"] = resource.download_override
    return data


# =====================================
# DASHBOARD
# =====================================

@admin_bp.route("/dashboard", methods=["GET"])
@admin_required
def dashboard():

    recent = Resource.query.order_by(
        Resource.created_at.desc()
    ).limit(5).all()

    now = datetime.utcnow()

    return jsonify({
        "status": "success",
        "stats": {
            "resources": Resource.query.count(),
            "books": Resource.query.filter_by(
                resource_type="book"
            ).count(),
            "videos": Resource.query.filter_by(
                resource_type="video"
            ).count(),
            "categories": Category.query.count(),
            "book_types": BookType.query.count(),
            "members": User.query.filter_by(
                role="member"
            ).count(),
            "new_messages": ContactMessage.query.filter_by(
                status="new"
            ).count(),
            "active_loans": Loan.query.filter_by(
                returned_at=None
            ).count(),
            "overdue_loans": Loan.query.filter(
                Loan.returned_at.is_(None),
                Loan.due_date < now
            ).count()
        },
        "recent_resources": [
            admin_resource_response(resource)
            for resource in recent
        ]
    }), 200


# =====================================
# CATEGORY MANAGEMENT
# =====================================

@admin_bp.route("/categories", methods=["GET"])
@admin_required
def list_categories():

    categories = Category.query.order_by(Category.name).all()

    return jsonify({
        "status": "success",
        "categories": [
            {
                "id": category.id,
                "name": category.name,
                "description": category.description,
                "allow_download": category.allow_download,
                "resource_count": len(category.resources)
            }
            for category in categories
        ]
    }), 200


@admin_bp.route("/categories", methods=["POST"])
@admin_required
def create_category():

    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    description = str(data.get("description", "")).strip()

    if not name:
        return jsonify({
            "status": "error",
            "message": "Category name is required."
        }), 400

    if Category.query.filter_by(name=name).first():
        return jsonify({
            "status": "error",
            "message": "This category already exists."
        }), 409

    category = Category(
        name=name,
        description=description or None,
        allow_download=parse_bool(data.get("allow_download"))
    )

    db.session.add(category)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Category created successfully.",
        "category": {
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "allow_download": category.allow_download,
            "resource_count": 0
        }
    }), 201


@admin_bp.route("/categories/<int:category_id>", methods=["PUT"])
@admin_required
def update_category(category_id):

    category = db.session.get(Category, category_id)

    if not category:
        return jsonify({
            "status": "error",
            "message": "Category not found."
        }), 404

    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    description = str(data.get("description", "")).strip()

    if not name:
        return jsonify({
            "status": "error",
            "message": "Category name is required."
        }), 400

    duplicate = Category.query.filter(
        Category.name == name,
        Category.id != category.id
    ).first()

    if duplicate:
        return jsonify({
            "status": "error",
            "message": "Another category already uses this name."
        }), 409

    category.name = name
    category.description = description or None
    category.allow_download = parse_bool(
        data.get("allow_download")
    )

    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Category updated successfully.",
        "category": {
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "allow_download": category.allow_download,
            "resource_count": len(category.resources)
        }
    }), 200


@admin_bp.route("/categories/<int:category_id>", methods=["DELETE"])
@admin_required
def delete_category(category_id):

    category = db.session.get(Category, category_id)

    if not category:
        return jsonify({
            "status": "error",
            "message": "Category not found."
        }), 404

    # A category in use cannot be deleted.
    if category.resources:
        return jsonify({
            "status": "error",
            "message": (
                "This category still contains resources. "
                "Move or delete them first."
            )
        }), 409

    db.session.delete(category)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Category deleted successfully."
    }), 200


# =====================================
# BOOK TYPE MANAGEMENT
# =====================================

@admin_bp.route("/book-types", methods=["GET"])
@admin_required
def list_book_types():

    types = BookType.query.order_by(BookType.name).all()

    return jsonify({
        "status": "success",
        "book_types": [
            {
                "id": book_type.id,
                "name": book_type.name,
                "description": book_type.description,
                "resource_count": Resource.query.filter_by(
                    resource_type=book_type.name
                ).count()
            }
            for book_type in types
        ]
    }), 200


@admin_bp.route("/book-types", methods=["POST"])
@admin_required
def create_book_type():

    data = request.get_json(silent=True) or {}

    name = normalize_type_name(data.get("name", ""))
    description = str(data.get("description", "")).strip()

    if not name:
        return jsonify({
            "status": "error",
            "message": "Book type name is required."
        }), 400

    if BookType.query.filter_by(name=name).first():
        return jsonify({
            "status": "error",
            "message": "This book type already exists."
        }), 409

    book_type = BookType(
        name=name,
        description=description or None
    )

    db.session.add(book_type)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Book type created successfully.",
        "book_type": {
            "id": book_type.id,
            "name": book_type.name,
            "description": book_type.description,
            "resource_count": 0
        }
    }), 201


@admin_bp.route("/book-types/<int:type_id>", methods=["PUT"])
@admin_required
def update_book_type(type_id):

    book_type = db.session.get(BookType, type_id)

    if not book_type:
        return jsonify({
            "status": "error",
            "message": "Book type not found."
        }), 404

    data = request.get_json(silent=True) or {}

    name = normalize_type_name(data.get("name", ""))
    description = str(data.get("description", "")).strip()

    if not name:
        return jsonify({
            "status": "error",
            "message": "Book type name is required."
        }), 400

    duplicate = BookType.query.filter(
        BookType.name == name,
        BookType.id != book_type.id
    ).first()

    if duplicate:
        return jsonify({
            "status": "error",
            "message": "Another book type already uses this name."
        }), 409

    old_name = book_type.name

    # Keep existing resources in sync when the type is renamed.
    if old_name != name:
        Resource.query.filter_by(
            resource_type=old_name
        ).update({"resource_type": name})

    book_type.name = name
    book_type.description = description or None

    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Book type updated successfully.",
        "book_type": {
            "id": book_type.id,
            "name": book_type.name,
            "description": book_type.description,
            "resource_count": Resource.query.filter_by(
                resource_type=book_type.name
            ).count()
        }
    }), 200


@admin_bp.route("/book-types/<int:type_id>", methods=["DELETE"])
@admin_required
def delete_book_type(type_id):

    book_type = db.session.get(BookType, type_id)

    if not book_type:
        return jsonify({
            "status": "error",
            "message": "Book type not found."
        }), 404

    # A type in use cannot be deleted.
    in_use = Resource.query.filter_by(
        resource_type=book_type.name
    ).count()

    if in_use:
        return jsonify({
            "status": "error",
            "message": (
                "This book type is used by existing resources. "
                "Change or delete them first."
            )
        }), 409

    db.session.delete(book_type)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Book type deleted successfully."
    }), 200


# =====================================
# RESOURCE MANAGEMENT
# =====================================

@admin_bp.route("/resources", methods=["GET"])
@admin_required
def list_resources():

    query = Resource.query

    # Optional search.
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

    # Optional category filter.
    category_id = request.args.get("category_id", type=int)

    if category_id is not None:
        query = query.filter_by(category_id=category_id)

    # Optional type filter.
    resource_type = request.args.get(
        "resource_type", ""
    ).strip().lower()

    if resource_type:
        query = query.filter_by(resource_type=resource_type)

    # Optional published filter.
    published = request.args.get(
        "is_published", ""
    ).strip().lower()

    if published in ("true", "false"):
        query = query.filter_by(
            is_published=(published == "true")
        )

    resources = query.order_by(
        Resource.created_at.desc()
    ).all()

    return jsonify({
        "status": "success",
        "resources": [
            admin_resource_response(resource)
            for resource in resources
        ]
    }), 200


# Apply validated form values and uploaded files to a resource.
def apply_resource_form(resource, form, files):

    title = form.get("title", "").strip()

    if not title:
        raise ValueError("Title is required.")

    resource_type = normalize_type_name(
        form.get("resource_type", "")
    )

    if not BookType.query.filter_by(name=resource_type).first():
        raise ValueError("Choose a valid book type.")

    category_id = form.get("category_id", type=int)
    category = (
        db.session.get(Category, category_id)
        if category_id else None
    )

    if not category:
        raise ValueError("Choose a valid category.")

    # Save new uploads before touching the database record.
    new_files = {}

    book_file = files.get("file")

    if book_file and book_file.filename:
        saved, error = save_upload(
            book_file, "books", BOOK_EXTENSIONS
        )

        if error:
            raise ValueError(error)

        new_files["file_path"] = saved

    cover_file = files.get("cover")

    if cover_file and cover_file.filename:
        saved, error = save_upload(
            cover_file, "covers", IMAGE_EXTENSIONS
        )

        if error:
            delete_upload(new_files.get("file_path"))
            raise ValueError(error)

        new_files["cover_image"] = saved

    resource.title = title
    resource.resource_type = resource_type
    resource.category = category
    resource.author = form.get("author", "").strip() or None
    resource.publisher = form.get("publisher", "").strip() or None
    resource.description = (
        form.get("description", "").strip() or None
    )
    resource.video_url = (
        form.get("video_url", "").strip() or None
    )

    if "download_override" in form:
        resource.download_override = parse_override(
            form.get("download_override")
        )

    if "is_published" in form:
        resource.is_published = parse_bool(
            form.get("is_published")
        )

    # Replace files and remove the old copies.
    if "file_path" in new_files:
        delete_upload(resource.file_path)
        resource.file_path = new_files["file_path"]

    if "cover_image" in new_files:
        delete_upload(resource.cover_image)
        resource.cover_image = new_files["cover_image"]


@admin_bp.route("/resources", methods=["POST"])
@admin_required
def create_resource():

    resource = Resource(is_published=False)

    try:
        apply_resource_form(
            resource, request.form, request.files
        )

    except ValueError as error:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": str(error)
        }), 400

    db.session.add(resource)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Resource created successfully.",
        "resource": admin_resource_response(resource)
    }), 201


@admin_bp.route(
    "/resources/<int:resource_id>",
    methods=["PUT"]
)
@admin_required
def update_resource(resource_id):

    resource = db.session.get(Resource, resource_id)

    if not resource:
        return jsonify({
            "status": "error",
            "message": "Resource not found."
        }), 404

    try:
        apply_resource_form(
            resource, request.form, request.files
        )

    except ValueError as error:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": str(error)
        }), 400

    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Resource updated successfully.",
        "resource": admin_resource_response(resource)
    }), 200


@admin_bp.route(
    "/resources/<int:resource_id>",
    methods=["DELETE"]
)
@admin_required
def delete_resource(resource_id):

    resource = db.session.get(Resource, resource_id)

    if not resource:
        return jsonify({
            "status": "error",
            "message": "Resource not found."
        }), 404

    # Remove the stored files as well.
    delete_upload(resource.file_path)
    delete_upload(resource.cover_image)

    db.session.delete(resource)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Resource deleted successfully."
    }), 200


# =====================================
# CATEGORY REPORT
# =====================================

@admin_bp.route("/reports/categories", methods=["GET"])
@admin_required
def category_report():

    rows = []
    totals = {
        "resources": 0,
        "books": 0,
        "videos": 0,
        "downloadable": 0
    }

    for category in Category.query.order_by(Category.name).all():

        resources = category.resources

        books = sum(
            1 for resource in resources
            if resource.resource_type == "book"
        )

        videos = sum(
            1 for resource in resources
            if resource.resource_type == "video"
        )

        downloadable = sum(
            1 for resource in resources
            if can_download(resource)
        )

        rows.append({
            "id": category.id,
            "name": category.name,
            "allow_download": category.allow_download,
            "resources": len(resources),
            "books": books,
            "videos": videos,
            "downloadable": downloadable
        })

        totals["resources"] += len(resources)
        totals["books"] += books
        totals["videos"] += videos
        totals["downloadable"] += downloadable

    return jsonify({
        "status": "success",
        "rows": rows,
        "totals": totals
    }), 200


# =====================================
# CONTACT MESSAGE INBOX
# =====================================

@admin_bp.route("/messages", methods=["GET"])
@admin_required
def list_messages():

    messages = ContactMessage.query.order_by(
        ContactMessage.created_at.desc()
    ).all()

    return jsonify({
        "status": "success",
        "messages": [
            {
                "id": message.id,
                "full_name": message.full_name,
                "email": message.email,
                "subject": message.subject,
                "message": message.message,
                "status": message.status,
                "created_at": (
                    message.created_at.isoformat()
                    if message.created_at else None
                )
            }
            for message in messages
        ]
    }), 200


@admin_bp.route(
    "/messages/<int:message_id>",
    methods=["PATCH"]
)
@admin_required
def update_message(message_id):

    message = db.session.get(ContactMessage, message_id)

    if not message:
        return jsonify({
            "status": "error",
            "message": "Message not found."
        }), 404

    data = request.get_json(silent=True) or {}
    status = str(data.get("status", "")).strip().lower()

    if status not in ("new", "read"):
        return jsonify({
            "status": "error",
            "message": "Status must be new or read."
        }), 400

    message.status = status
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Message updated successfully."
    }), 200


@admin_bp.route(
    "/messages/<int:message_id>",
    methods=["DELETE"]
)
@admin_required
def delete_message(message_id):

    message = db.session.get(ContactMessage, message_id)

    if not message:
        return jsonify({
            "status": "error",
            "message": "Message not found."
        }), 404

    db.session.delete(message)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Message deleted successfully."
    }), 200


# =====================================
# USER MANAGEMENT
# =====================================

@admin_bp.route("/users", methods=["GET"])
@admin_required
def list_users():

    users = User.query.order_by(User.created_at.desc()).all()

    return jsonify({
        "status": "success",
        "users": [
            {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "role": user.role,
                "is_active": user.is_active,
                "created_at": (
                    user.created_at.isoformat()
                    if user.created_at else None
                )
            }
            for user in users
        ]
    }), 200


@admin_bp.route("/users/<int:user_id>", methods=["PATCH"])
@admin_required
def update_user(user_id):

    user = db.session.get(User, user_id)

    if not user:
        return jsonify({
            "status": "error",
            "message": "User not found."
        }), 404

    current_admin = get_logged_in_user()

    data = request.get_json(silent=True) or {}

    # Administrators cannot deactivate their own account.
    if user.id == current_admin.id and "is_active" in data:
        if not parse_bool(data.get("is_active"), True):
            return jsonify({
                "status": "error",
                "message": "You cannot deactivate your own account."
            }), 400

    if "is_active" in data:
        user.is_active = parse_bool(data.get("is_active"))

    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "User updated successfully.",
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active
        }
    }), 200


@admin_bp.route(
    "/users/<int:user_id>/reset-password",
    methods=["POST"]
)
@admin_required
def reset_user_password(user_id):

    user = db.session.get(User, user_id)

    if not user:
        return jsonify({
            "status": "error",
            "message": "User not found."
        }), 404

    data = request.get_json(silent=True) or {}
    new_password = data.get("new_password", "")

    if len(new_password) < 8 or len(new_password) > 128:
        return jsonify({
            "status": "error",
            "message": "Password must be between 8 and 128 characters."
        }), 400

    # Administrators can recover a member's password.
    user.password_hash = generate_password_hash(new_password)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Password reset successfully."
    }), 200


# =====================================
# ADMIN PROFILE
# =====================================

@admin_bp.route("/profile", methods=["GET"])
@admin_required
def get_profile():

    return jsonify({
        "status": "success",
        "user": user_response(get_logged_in_user())
    }), 200


@admin_bp.route("/profile", methods=["PUT"])
@admin_required
def update_profile():

    admin = get_logged_in_user()

    data = request.get_json(silent=True) or {}

    full_name = str(data.get("full_name", "")).strip()
    email = str(data.get("email", "")).strip().lower()

    if not full_name or not email:
        return jsonify({
            "status": "error",
            "message": "Full name and email are required."
        }), 400

    if "@" not in email or "." not in email.split("@")[-1]:
        return jsonify({
            "status": "error",
            "message": "Enter a valid email address."
        }), 400

    duplicate = User.query.filter(
        User.email == email,
        User.id != admin.id
    ).first()

    if duplicate:
        return jsonify({
            "status": "error",
            "message": "This email is already in use."
        }), 409

    admin.full_name = full_name
    admin.email = email
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Profile updated successfully.",
        "user": user_response(admin)
    }), 200


# =====================================
# LOAN MANAGEMENT
# =====================================

@admin_bp.route("/loans", methods=["GET"])
@admin_required
def list_loans():

    status = request.args.get("status", "all").strip().lower()

    query = Loan.query

    now = datetime.utcnow()

    if status == "active":
        query = query.filter(Loan.returned_at.is_(None))
    elif status == "overdue":
        query = query.filter(
            Loan.returned_at.is_(None),
            Loan.due_date < now
        )
    elif status == "returned":
        query = query.filter(Loan.returned_at.isnot(None))

    loans = query.order_by(Loan.borrowed_at.desc()).limit(300).all()

    results = []

    for loan in loans:
        entry = loan_response(loan)
        entry["member"] = {
            "id": loan.user.id,
            "full_name": loan.user.full_name,
            "email": loan.user.email
        }
        results.append(entry)

    return jsonify({
        "status": "success",
        "loans": results
    }), 200


@admin_bp.route("/loans/<int:loan_id>/return", methods=["POST"])
@admin_required
def admin_return_loan(loan_id):

    loan = db.session.get(Loan, loan_id)

    if not loan:
        return jsonify({
            "status": "error",
            "message": "Loan not found."
        }), 404

    if loan.returned_at is not None:
        return jsonify({
            "status": "error",
            "message": "This loan has already been returned."
        }), 409

    loan.returned_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": (
            f'"{loan.resource.title}" was marked as returned.'
        )
    }), 200
