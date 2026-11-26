
# Shared fixtures for the backend tests.
#
# The suite runs entirely on an in-memory SQLite database, so CI needs
# no MySQL service. Run from the backend folder:
#   ../.venv/Scripts/python.exe -m pytest -q

import sys
from pathlib import Path

import pytest
from werkzeug.security import generate_password_hash

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from extensions import db  # noqa: E402
from models import BookType, Category, Resource, User  # noqa: E402
from run import create_app  # noqa: E402


class TestConfig:
    TESTING = True
    SECRET_KEY = "test-secret-key"
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_SECURE = False


def make_user(full_name, email, password, role="member"):
    return User(
        full_name=full_name,
        email=email,
        password_hash=generate_password_hash(password),
        role=role
    )


@pytest.fixture()
def app(tmp_path, monkeypatch):
    # resolve_file() and the upload endpoints read Config.UPLOAD_FOLDER
    # at call time, so point it at a scratch folder for the tests.
    import library
    monkeypatch.setattr(library.Config, "UPLOAD_FOLDER", str(tmp_path))

    application = create_app(TestConfig)
    application.config.update(UPLOAD_FOLDER=str(tmp_path))

    with application.app_context():
        db.create_all()

        tech = Category(
            name="Technology", allow_download=True, description="Tech"
        )
        lit = Category(
            name="Literature", allow_download=False, description="Books"
        )
        locked = Category(
            name="Archive", allow_download=False, description="Restricted"
        )
        db.session.add_all([tech, lit, locked])
        db.session.add_all([
            BookType(name="book"), BookType(name="video")
        ])
        db.session.flush()

        # Enough published books to exercise offset/limit paging.
        for index in range(16):
            db.session.add(Resource(
                title=f"Test Book {index:02d}",
                author=f"Author {index}",
                resource_type="book",
                category_id=tech.id if index % 2 else lit.id,
                is_published=True
            ))

        db.session.add(Resource(
            title="Test Video",
            author="Tester",
            resource_type="video",
            category_id=tech.id,
            video_url="https://www.youtube.com/watch?v=abc123",
            is_published=True
        ))
        db.session.add(Resource(
            title="Hidden Book",
            author="Nobody",
            resource_type="book",
            category_id=tech.id,
            is_published=False
        ))

        # A book with a real PDF on disk to test reading and downloading.
        pdf = tmp_path / "books" / "sample.pdf"
        pdf.parent.mkdir(parents=True)
        pdf.write_bytes(b"%PDF-1.4\n% test\n%%EOF\n")

        db.session.add(Resource(
            title="Readable Book",
            author="Writer",
            resource_type="book",
            category_id=tech.id,
            file_path="books/sample.pdf",
            is_published=True
        ))
        db.session.add(Resource(
            title="Restricted Book",
            author="Writer",
            resource_type="book",
            category_id=locked.id,
            file_path="books/sample.pdf",
            is_published=True
        ))

        db.session.add_all([
            make_user("Admin User", "admin@test.local", "AdminPass123", "admin"),
            make_user("Member User", "member@test.local", "MemberPass123")
        ])
        db.session.commit()

        yield application

        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def login(client, email="member@test.local", password="MemberPass123"):
    response = client.post(
        "/api/auth/login",
        json={"email": email, "password": password}
    )
    assert response.status_code == 200, response.get_json()
    return response


@pytest.fixture()
def member(client):
    login(client)
    return client


@pytest.fixture()
def admin(client):
    login(client, "admin@test.local", "AdminPass123")
    return client
