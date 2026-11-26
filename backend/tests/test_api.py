
# API tests for the E-Library backend (SQLite, no MySQL needed).

from datetime import datetime

from conftest import login
from extensions import db
from models import Category, ContactMessage, Loan, Resource, Review


def resource_id(client, title):
    response = client.get(f"/api/resources?search={title}")
    matches = [
        item for item in response.get_json()["resources"]
        if item["title"] == title
    ]
    assert matches, f"{title} not found"
    return matches[0]["id"]


# =====================================
# Health & public catalogue
# =====================================

def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "success"


def test_stats_counts_only_published(client):
    stats = client.get("/api/stats").get_json()["stats"]
    assert stats["resources"] == 19
    assert stats["books"] == 18
    assert stats["videos"] == 1
    assert stats["categories"] == 3


def test_resources_paging(client):
    first = client.get("/api/resources?limit=5&offset=0").get_json()
    second = client.get("/api/resources?limit=5&offset=5").get_json()
    last = client.get("/api/resources?limit=5&offset=15").get_json()

    assert first["total"] == 19
    assert first["has_more"] is True
    assert len(first["resources"]) == 5
    assert len(second["resources"]) == 5
    assert first["resources"][0]["id"] != second["resources"][0]["id"]
    assert len(last["resources"]) == 4
    assert last["has_more"] is False


def test_resources_paging_is_stable(client):
    page_one = client.get("/api/resources?limit=4").get_json()
    page_two = client.get("/api/resources?limit=4&offset=4").get_json()
    ids = [item["id"] for item in page_one["resources"]]
    ids += [item["id"] for item in page_two["resources"]]
    assert len(ids) == len(set(ids))


def test_resource_filters(client):
    videos = client.get("/api/resources?resource_type=video").get_json()
    assert [item["title"] for item in videos["resources"]] == ["Test Video"]

    by_author = client.get("/api/resources?search=Author 3").get_json()
    assert by_author["total"] >= 1
    assert all("Author" in item["author"] for item in by_author["resources"])

    by_category = client.get("/api/resources?category_id=2").get_json()
    assert by_category["total"] == 8


def test_hidden_resource_is_not_listed(client):
    response = client.get("/api/resources?search=Hidden Book")
    assert response.get_json()["total"] == 0


def test_resource_detail(client):
    book_id = resource_id(client, "Test Book 00")
    ok = client.get(f"/api/resources/{book_id}")
    assert ok.status_code == 200
    assert ok.get_json()["resource"]["title"] == "Test Book 00"
    assert client.get("/api/resources/9999").status_code == 404


def test_media_blocks_path_traversal(client):
    response = client.get("/api/media/../config.py")
    assert response.status_code in (400, 404)


# =====================================
# Accounts
# =====================================

def test_register_validation(client):
    assert client.post("/api/auth/register", json={}).status_code == 400
    assert client.post("/api/auth/register", json={
        "full_name": "A", "email": "bad", "password": "longenough"
    }).status_code == 400
    assert client.post("/api/auth/register", json={
        "full_name": "A", "email": "a@b.co", "password": "short"
    }).status_code == 400


def test_register_and_login(client):
    created = client.post("/api/auth/register", json={
        "full_name": "New Member",
        "email": "new@test.local",
        "password": "NewPass123"
    })
    assert created.status_code == 201

    duplicate = client.post("/api/auth/register", json={
        "full_name": "New Member",
        "email": "new@test.local",
        "password": "NewPass123"
    })
    assert duplicate.status_code == 409

    assert client.post("/api/auth/login", json={
        "email": "new@test.local", "password": "wrong-pass"
    }).status_code == 401

    login(client, "new@test.local", "NewPass123")

    me = client.get("/api/auth/me").get_json()
    assert me["user"]["email"] == "new@test.local"

    client.post("/api/auth/logout")
    assert client.get("/api/auth/me").status_code == 401


# =====================================
# Shelf (favourites)
# =====================================

def test_favorites_require_login(client):
    book_id = resource_id(client, "Test Book 00")
    assert client.get("/api/favorites").status_code == 401
    assert client.post(f"/api/favorites/{book_id}").status_code == 401


def test_favorite_lifecycle(member):
    book_id = resource_id(member, "Test Book 01")

    assert member.post(f"/api/favorites/{book_id}").status_code == 200
    shelf = member.get("/api/favorites").get_json()["favorites"]
    assert [item["id"] for item in shelf] == [book_id]

    # Adding twice must not duplicate the shelf entry.
    member.post(f"/api/favorites/{book_id}")
    assert len(member.get("/api/favorites").get_json()["favorites"]) == 1

    assert member.delete(f"/api/favorites/{book_id}").status_code == 200
    assert member.get("/api/favorites").get_json()["favorites"] == []


# =====================================
# Loans
# =====================================

def test_borrow_rules(member):
    video_id = resource_id(member, "Test Video")
    assert member.post("/api/loans", json={
        "resource_id": video_id
    }).status_code == 400

    first = resource_id(member, "Test Book 00")
    created = member.post("/api/loans", json={"resource_id": first})
    assert created.status_code == 201
    loan = created.get_json()["loan"]
    assert loan["status"] == "active"
    assert loan["returned_at"] is None

    duplicate = member.post("/api/loans", json={"resource_id": first})
    assert duplicate.status_code == 409


def test_loan_limit(client):
    login(client)
    created = 0

    for index in range(6):
        book_id = resource_id(client, f"Test Book {index:02d}")
        response = client.post("/api/loans", json={"resource_id": book_id})
        if response.status_code == 201:
            created += 1
        else:
            assert response.status_code == 409

    assert created == 5


def test_loan_return_and_history(member):
    book_id = resource_id(member, "Test Book 02")
    loan = member.post(
        "/api/loans", json={"resource_id": book_id}
    ).get_json()["loan"]

    mine = member.get("/api/loans/mine").get_json()
    assert [item["id"] for item in mine["active"]] == [loan["id"]]

    returned = member.post(f"/api/loans/{loan['id']}/return")
    assert returned.status_code == 200

    after = member.get("/api/loans/mine").get_json()
    assert after["active"] == []
    assert [item["id"] for item in after["history"]] == [loan["id"]]

    assert member.post(f"/api/loans/{loan['id']}/return").status_code == 409


def test_cannot_return_someone_elses_loan(client, app):
    login(client)
    book_id = resource_id(client, "Test Book 03")
    loan = client.post(
        "/api/loans", json={"resource_id": book_id}
    ).get_json()["loan"]

    other = app.test_client()
    login(other, "admin@test.local", "AdminPass123")
    assert other.post(f"/api/loans/{loan['id']}/return").status_code == 404


# =====================================
# Reviews
# =====================================

def test_review_lifecycle(member):
    book_id = resource_id(member, "Test Book 04")

    assert member.post(
        f"/api/resources/{book_id}/reviews", json={"rating": 6}
    ).status_code == 400

    saved = member.post(
        f"/api/resources/{book_id}/reviews",
        json={"rating": 5, "comment": "Excellent"}
    )
    assert saved.status_code == 200

    # Posting again updates the same review instead of duplicating it.
    member.post(
        f"/api/resources/{book_id}/reviews",
        json={"rating": 4, "comment": "Still good"}
    )

    reviews = member.get(
        f"/api/resources/{book_id}/reviews"
    ).get_json()["reviews"]
    assert len(reviews) == 1
    assert reviews[0]["rating"] == 4

    detail = member.get(f"/api/resources/{book_id}").get_json()["resource"]
    assert detail["average_rating"] == 4.0
    assert detail["rating_count"] == 1

    assert member.delete(
        f"/api/resources/{book_id}/reviews/mine"
    ).status_code == 200
    assert member.get(f"/api/resources/{book_id}/reviews").get_json()[
        "reviews"
    ] == []


def test_reviews_need_login(client):
    book_id = resource_id(client, "Test Book 05")
    assert client.post(
        f"/api/resources/{book_id}/reviews", json={"rating": 5}
    ).status_code == 401


# =====================================
# Reading & downloads
# =====================================

def test_read_requires_login(client):
    book_id = resource_id(client, "Readable Book")
    assert client.get(f"/api/resources/{book_id}/read").status_code == 401


def test_read_and_download_permissions(member):
    readable = resource_id(member, "Readable Book")
    assert len(member.get(f"/api/resources/{readable}/read").data) > 0
    assert len(member.get(f"/api/resources/{readable}/download").data) > 0

    restricted = resource_id(member, "Restricted Book")
    assert member.get(
        f"/api/resources/{restricted}/download"
    ).status_code == 403


def test_remote_book_reads_at_its_source(app, member):
    source = "https://www.gutenberg.org/ebooks/1342.html.images"

    with app.app_context():
        category = Category.query.filter_by(name="Technology").first()
        db.session.add(Resource(
            title="Remote Classic",
            author="Public Domain",
            resource_type="book",
            category=category,
            external_url=source,
            cover_image="https://www.gutenberg.org/cover.jpg",
            slug="gutenberg-1342",
            is_published=True
        ))
        db.session.commit()

    listing = member.get(
        "/api/resources?search=Remote Classic"
    ).get_json()
    remote = listing["resources"][0]

    assert remote["is_remote"] is True
    assert remote["readable"] is True
    assert remote["can_borrow"] is False
    assert remote["can_download"] is False
    assert remote["external_url"] == source

    opened = member.get(f"/api/resources/{remote['id']}/read")
    assert opened.status_code == 302
    assert opened.headers["Location"] == source

    assert member.get(
        f"/api/resources/{remote['id']}/download"
    ).status_code == 400
    assert member.post(
        "/api/loans",
        json={"resource_id": remote["id"]}
    ).status_code == 400


def test_public_domain_scan_link_is_allowed(app, member):
    source = "https://archive.org/details/lilithromance00macd"

    with app.app_context():
        category = Category.query.filter_by(name="Literature").first()
        db.session.add(Resource(
            title="Public Domain Fantasy Scan",
            author="George MacDonald",
            resource_type="book",
            category=category,
            external_url=source,
            cover_image="covers/ol-123.jpg",
            slug="ol-123",
            is_published=True
        ))
        db.session.commit()

    listing = member.get(
        "/api/resources?search=Public Domain Fantasy Scan"
    ).get_json()
    remote = listing["resources"][0]

    assert remote["is_remote"] is True
    assert member.get(
        f"/api/resources/{remote['id']}/read"
    ).headers["Location"] == source


# =====================================
# Contact & admin
# =====================================

def test_contact_message(client, app):
    assert client.post("/api/contact", json={}).status_code == 400

    sent = client.post("/api/contact", json={
        "full_name": "Visitor",
        "email": "visitor@test.local",
        "subject": "Hello",
        "message": "Question about membership."
    })
    assert sent.status_code == 201

    with app.app_context():
        assert ContactMessage.query.count() == 1


def test_admin_guard(app):
    guest = app.test_client()
    member = app.test_client()
    admin = app.test_client()

    login(member)
    login(admin, "admin@test.local", "AdminPass123")

    assert guest.get("/api/admin/dashboard").status_code == 401
    assert member.get("/api/admin/dashboard").status_code == 403
    dashboard = admin.get("/api/admin/dashboard")
    assert dashboard.status_code == 200

    created = admin.post("/api/admin/categories", json={
        "name": "New Topic", "description": "Added by test"
    })
    assert created.status_code == 201

    with app.app_context():
        assert Category.query.filter_by(name="New Topic").first()


def test_admin_rejects_untrusted_external_link(app, admin):
    with app.app_context():
        category_id = Category.query.first().id

    response = admin.post("/api/admin/resources", data={
        "title": "Bad Link",
        "resource_type": "book",
        "category_id": str(category_id),
        "external_url": "https://untrusted.example/book"
    })

    assert response.status_code == 400
    assert "approved public-domain source" in response.get_json()["message"]
