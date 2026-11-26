
# Import datetime for recording creation dates.
from datetime import datetime

# Import the shared database instance.
from extensions import db


# =====================================
# 1. USER MODEL
# Stores members and administrators.
# =====================================

class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column(
        db.String(120),
        nullable=False
    )

    email = db.Column(
        db.String(255),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    # Available roles: member and admin.
    role = db.Column(
        db.String(20),
        default="member",
        nullable=False
    )

    is_active = db.Column(
        db.Boolean,
        default=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def __repr__(self):
        return f"<User {self.email}>"


# =====================================
# 2. CATEGORY MODEL
# Stores library categories.
# =====================================

class Category(db.Model):

    __tablename__ = "categories"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    # Downloads are disabled by default.
    allow_download = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    # Connect categories to their resources.
    resources = db.relationship(
        "Resource",
        back_populates="category"
    )

    def __repr__(self):
        return f"<Category {self.name}>"


# =====================================
# 3. BOOK TYPE MODEL
# Stores the allowed resource types (Book/Video).
# =====================================

class BookType(db.Model):

    __tablename__ = "book_types"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def __repr__(self):
        return f"<BookType {self.name}>"


# =====================================
# 4. RESOURCE MODEL
# Stores books and video tutorials.
# =====================================

class Resource(db.Model):

    __tablename__ = "resources"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    # Stable catalogue identity used by the seed script. Unlike the title,
    # a slug never changes when a book is refreshed or renamed upstream.
    slug = db.Column(
        db.String(100),
        unique=True,
        nullable=True,
        index=True
    )

    # Resource type can be book or video.
    resource_type = db.Column(
        db.String(20),
        nullable=False,
        default="book"
    )

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id"),
        nullable=False
    )

    author = db.Column(
        db.String(150),
        nullable=True
    )

    publisher = db.Column(
        db.String(150),
        nullable=True
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    # Location of the uploaded book file.
    file_path = db.Column(
        db.String(500),
        nullable=True
    )

    # Location of the book cover image.
    cover_image = db.Column(
        db.String(500),
        nullable=True
    )

    # External or embedded video location.
    video_url = db.Column(
        db.String(500),
        nullable=True
    )

    # Reading link for books that are streamed from an open source
    # (for example Project Gutenberg) rather than stored locally.
    external_url = db.Column(
        db.String(500),
        nullable=True
    )

    # None means inherit category permission.
    download_override = db.Column(
        db.Boolean,
        nullable=True
    )

    is_published = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    # Establish the category relationship.
    category = db.relationship(
        "Category",
        back_populates="resources"
    )

    def __repr__(self):
        return f"<Resource {self.title}>"


# =====================================
# 5. CONTACT MESSAGE MODEL
# Stores visitor enquiries.
# =====================================

class ContactMessage(db.Model):

    __tablename__ = "contact_messages"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    full_name = db.Column(
        db.String(120),
        nullable=False
    )

    email = db.Column(
        db.String(255),
        nullable=False
    )

    subject = db.Column(
        db.String(200),
        nullable=False
    )

    message = db.Column(
        db.Text,
        nullable=False
    )

    status = db.Column(
        db.String(20),
        default="new",
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def __repr__(self):
        return f"<ContactMessage {self.id}>"


# =====================================
# 6. FAVORITE MODEL
# Saves books and videos to a member's shelf.
# =====================================

class Favorite(db.Model):

    __tablename__ = "favorites"

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "resource_id",
            name="uq_favorite_user_resource"
        ),
    )

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    resource_id = db.Column(
        db.Integer,
        db.ForeignKey("resources.id"),
        nullable=False,
        index=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    resource = db.relationship("Resource")

    def __repr__(self):
        return f"<Favorite user={self.user_id} resource={self.resource_id}>"


# =====================================
# 7. LOAN MODEL
# Tracks books borrowed by members.
# =====================================

class Loan(db.Model):

    __tablename__ = "loans"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    resource_id = db.Column(
        db.Integer,
        db.ForeignKey("resources.id"),
        nullable=False,
        index=True
    )

    borrowed_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    due_date = db.Column(
        db.DateTime,
        nullable=False
    )

    returned_at = db.Column(
        db.DateTime,
        nullable=True
    )

    user = db.relationship("User")
    resource = db.relationship("Resource")

    @property
    def is_active(self):
        return self.returned_at is None

    @property
    def is_overdue(self):
        return (
            self.returned_at is None
            and self.due_date < datetime.utcnow()
        )

    def __repr__(self):
        return f"<Loan user={self.user_id} resource={self.resource_id}>"


# =====================================
# 8. REVIEW MODEL
# One rating + comment per member per resource.
# =====================================

class Review(db.Model):

    __tablename__ = "reviews"

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "resource_id",
            name="uq_review_user_resource"
        ),
    )

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    resource_id = db.Column(
        db.Integer,
        db.ForeignKey("resources.id"),
        nullable=False,
        index=True
    )

    rating = db.Column(
        db.Integer,
        nullable=False
    )

    comment = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    user = db.relationship("User")

    def __repr__(self):
        return f"<Review user={self.user_id} resource={self.resource_id}>"
