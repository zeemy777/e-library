
# Sample data for local testing and demonstration.
# Running this script more than once will not create duplicates.

from run import create_app
from extensions import db
from models import BookType, Category, Resource, User
from werkzeug.security import generate_password_hash


# Create the Flask application and work inside its context.
app = create_app()

with app.app_context():

    # Make sure the tables exist.
    db.create_all()

    # Default resource types managed by the admin.
    default_types = [
        ("book", "A readable or downloadable book."),
        ("video", "A video tutorial resource.")
    ]

    for name, description in default_types:

        if not BookType.query.filter_by(name=name).first():
            db.session.add(
                BookType(name=name, description=description)
            )

    # Default administrator account for the assignment demo.
    admin_email = "admin@elibrary.com"

    if not User.query.filter_by(email=admin_email).first():
        db.session.add(
            User(
                full_name="Library Admin",
                email=admin_email,
                password_hash=generate_password_hash("Admin@12345"),
                role="admin"
            )
        )

    db.session.commit()

    # Stop if sample resources were already added.
    if Resource.query.count() > 0:
        print("Resources already exist. Admin and types are ready.")
        raise SystemExit(0)

    # Retrieve or create the default categories.
    category_settings = {
        "Technology": True,
        "Science": True,
        "Business": True,
        "Literature": False
    }

    categories = {}

    for name, allow_download in category_settings.items():

        category = Category.query.filter_by(name=name).first()

        if not category:
            category = Category(
                name=name,
                allow_download=allow_download
            )
            db.session.add(category)

        categories[name] = category

    db.session.flush()

    # Sample books and video tutorials.
    sample_resources = [
        {
            "title": "Clean Code",
            "resource_type": "book",
            "category": "Technology",
            "author": "Robert C. Martin",
            "publisher": "Prentice Hall",
            "description": (
                "A handbook of agile software craftsmanship "
                "with practical advice on writing readable code."
            )
        },
        {
            "title": "Python Crash Course",
            "resource_type": "book",
            "category": "Technology",
            "author": "Eric Matthes",
            "publisher": "No Starch Press",
            "description": (
                "A hands-on introduction to programming "
                "using Python, projects included."
            )
        },
        {
            "title": "A Brief History of Time",
            "resource_type": "book",
            "category": "Science",
            "author": "Stephen Hawking",
            "publisher": "Bantam Books",
            "description": (
                "An accessible journey through cosmology, "
                "black holes and the origins of the universe."
            )
        },
        {
            "title": "The Lean Startup",
            "resource_type": "book",
            "category": "Business",
            "author": "Eric Ries",
            "publisher": "Crown Business",
            "description": (
                "How today's entrepreneurs use validated "
                "learning to build successful businesses."
            )
        },
        {
            "title": "Things Fall Apart",
            "resource_type": "book",
            "category": "Literature",
            "author": "Chinua Achebe",
            "publisher": "Heinemann",
            "description": (
                "A classic novel about tradition, change and "
                "colonialism in pre-colonial Nigeria."
            )
        },
        {
            "title": "Getting Started with Web Development",
            "resource_type": "video",
            "category": "Technology",
            "author": "E-Library Team",
            "publisher": "E-Library",
            "description": (
                "A short sample tutorial video used to test "
                "video playback in the catalogue."
            ),
            "video_url": (
                "https://interactive-examples.mdn.mozilla.net/"
                "media/cc0-videos/flower.mp4"
            )
        },
        {
            "title": "Introduction to Science",
            "resource_type": "video",
            "category": "Science",
            "author": "E-Library Team",
            "publisher": "E-Library",
            "description": (
                "A sample science tutorial video used to test "
                "the video catalogue filter."
            ),
            "video_url": "https://www.w3schools.com/html/mov_bbb.mp4"
        }
    ]

    # Insert each sample resource.
    for item in sample_resources:

        resource = Resource(
            title=item["title"],
            resource_type=item["resource_type"],
            category=categories[item["category"]],
            author=item.get("author"),
            publisher=item.get("publisher"),
            description=item.get("description"),
            video_url=item.get("video_url"),
            is_published=True
        )

        db.session.add(resource)

    db.session.commit()

    print(
        "Sample data added:",
        Resource.query.count(),
        "resources and",
        Category.query.count(),
        "categories."
    )
