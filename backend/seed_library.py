# Populate the library with the real catalogue and its book files.
#
# Run after tools/build_library_assets.py:
#   ../.venv/Scripts/python.exe seed_library.py
#
# The script is safe to run more than once. It upgrades the original
# seven demo rows in place and adds anything that is still missing.

import json
from pathlib import Path

from werkzeug.security import generate_password_hash

from config import Config
from extensions import db
from library_catalogue import BOOKS, CATEGORIES, VIDEOS
from models import BookType, Category, Resource, User
from run import create_app
from schema import ensure_resource_columns

BASE_DIR = Path(__file__).resolve().parent

app = create_app()

UPLOAD_DIR = Path(Config.UPLOAD_FOLDER)

# The original demo rows keep their ids (and any saved favourites),
# but now point at real, openly licensed editions.
LEGACY_TITLES = {
    "Clean Code": "think-python-2e",
    "Python Crash Course": "think-stats-2e",
    "A Brief History of Time": "origin-of-species",
    "The Lean Startup": "wealth-of-nations",
    "Things Fall Apart": "pride-and-prejudice",
    "Getting Started with Web Development": "python-for-beginners",
    "Introduction to Science": "crash-course-biology"
}


def file_exists(relative_path):
    return (UPLOAD_DIR / relative_path).is_file()


def load_catalogue_file(name):
    # Generated catalogue files are committed with the repo, so seeding
    # never needs a network connection.
    path = BASE_DIR / "catalogue" / name

    if not path.is_file():
        return []

    data = json.loads(path.read_text(encoding="utf-8"))

    return data.get("books", [])


def load_remote_books():
    books = load_catalogue_file("remote_books.json")
    books.extend(load_catalogue_file("fantasy_books.json"))
    books.extend(load_catalogue_file("subject_books.json"))
    return books


def seed_users():
    default_types = [
        ("book", "A readable or downloadable book."),
        ("video", "A video tutorial resource.")
    ]

    for name, description in default_types:
        if not BookType.query.filter_by(name=name).first():
            db.session.add(
                BookType(name=name, description=description)
            )

    admin = User.query.filter_by(email="admin@elibrary.com").first()

    if not admin:
        db.session.add(
            User(
                full_name="Library Admin",
                email="admin@elibrary.com",
                password_hash=generate_password_hash("Admin@12345"),
                role="admin"
            )
        )

    member = User.query.filter_by(email="member@elibrary.com").first()

    if not member:
        db.session.add(
            User(
                full_name="Demo Member",
                email="member@elibrary.com",
                password_hash=generate_password_hash("Member@12345"),
                role="member"
            )
        )


def seed_categories():
    categories = {}

    for item in CATEGORIES:
        category = Category.query.filter_by(name=item["name"]).first()

        if not category:
            category = Category(name=item["name"])
            db.session.add(category)

        category.description = item["description"]
        category.allow_download = item["allow_download"]
        categories[item["name"]] = category

    db.session.flush()
    return categories


def apply_book(resource, book, categories):
    remote = book.get("source") == "remote"

    resource.slug = book["slug"]
    resource.title = book["title"]
    resource.resource_type = "book"
    resource.category = categories[book["category"]]
    resource.author = book["author"]
    resource.publisher = book["publisher"]
    resource.description = book["description"]
    resource.download_override = None
    resource.is_published = True
    resource.video_url = None
    resource.external_url = (
        book.get("external_url") if remote else None
    )

    if remote:
        # Streamed books have no local PDF. Their cover is a real public-domain
        # scan where one was found, with a generated SVG as the last fallback.
        resource.file_path = None
        resource.cover_image = book.get("cover_image")
        return

    pdf_path = f"books/{book['slug']}.pdf"
    resource.file_path = pdf_path if file_exists(pdf_path) else None

    cover_path = f"covers/{book['slug']}.jpg"
    resource.cover_image = cover_path if file_exists(cover_path) else None


def apply_video(resource, video, categories):
    resource.slug = video["slug"]
    resource.title = video["title"]
    resource.resource_type = "video"
    resource.category = categories[video["category"]]
    resource.author = video["author"]
    resource.publisher = video["publisher"]
    resource.description = video["description"]
    resource.download_override = None
    resource.is_published = True
    resource.file_path = None
    resource.external_url = None

    video_url = video["video_url"]
    if video_url.startswith("videos/"):
        resource.video_url = video_url if file_exists(video_url) else None
    else:
        resource.video_url = video_url

    cover_path = f"covers/{video['slug']}.jpg"
    resource.cover_image = cover_path if file_exists(cover_path) else None


def main():
    with app.app_context():
        db.create_all()
        ensure_resource_columns()
        seed_users()
        categories = seed_categories()

        catalogue = {
            item["slug"]: ("book", item)
            for item in BOOKS
        }
        catalogue.update({
            item["slug"]: ("book", item)
            for item in load_remote_books()
        })
        catalogue.update({
            item["slug"]: ("video", item)
            for item in VIDEOS
        })

        # Generated rows are owned by the committed catalogues. If an entry is
        # removed (for example a misclassified scan), retire its old row so a
        # re-seed reflects the current files. Unpublishing keeps any saved
        # favourites and loan history intact.
        retired = 0
        generated_prefixes = ("gutenberg-", "ol-")

        for resource in Resource.query.filter_by(is_published=True).all():
            slug = resource.slug or ""

            if (
                slug.startswith(generated_prefixes)
                and slug not in catalogue
                and resource.external_url
            ):
                resource.is_published = False
                retired += 1

        # Rename only the original sample rows so their ids stay intact.
        # A title-only lookup also matches generated catalogue rows with the
        # same name (MySQL collations are case-insensitive), which can steal
        # their slug and break the unique constraint during a re-seed.
        for legacy_title, slug in LEGACY_TITLES.items():
            resource = Resource.query.filter(
                Resource.id <= len(LEGACY_TITLES),
                Resource.title == legacy_title
            ).first()

            if not resource:
                continue

            kind, item = catalogue[slug]

            if kind == "book":
                apply_book(resource, item, categories)
            else:
                apply_video(resource, item, categories)

        db.session.flush()

        added = 0
        updated = 0

        for kind, item in catalogue.values():
            # Slug is the stable key. Titles are only a fallback for rows
            # created before slugs existed.
            resource = Resource.query.filter_by(
                slug=item["slug"]
            ).first()

            if not resource:
                # Only rows created before slugs existed may be matched by
                # title. Never hijack an admin-created resource that already
                # has its own identity.
                resource = Resource.query.filter_by(
                    title=item["title"],
                    slug=None
                ).first()

            if not resource:
                resource = Resource(
                    title=item["title"],
                    resource_type=kind,
                    category=categories[item["category"]],
                    is_published=True
                )
                db.session.add(resource)
                added += 1
            else:
                updated += 1

            if kind == "book":
                apply_book(resource, item, categories)
            else:
                apply_video(resource, item, categories)

        db.session.commit()

        total = Resource.query.filter_by(is_published=True).count()
        books = Resource.query.filter_by(
            resource_type="book",
            is_published=True
        ).count()
        videos = Resource.query.filter_by(
            resource_type="video",
            is_published=True
        ).count()

        missing_files = [
            resource.title
            for resource in Resource.query.filter_by(
                resource_type="book",
                is_published=True
            ).all()
            if not resource.external_url
            and (not resource.file_path
                 or not file_exists(resource.file_path))
        ]

        print(
            f"Catalogue ready: {total} published resources "
            f"({books} books, {videos} videos) across "
            f"{Category.query.count()} categories."
        )
        print(
            f"Added {added} new rows, refreshed {updated} existing rows "
            f"and retired {retired} removed generated rows."
        )

        if missing_files:
            print("Books without a file on disk:")
            for title in missing_files:
                print(f"  - {title}")
        else:
            print(
                "Every local book has a readable PDF on disk "
                "(remote books stream from their source)."
            )


if __name__ == "__main__":
    main()
