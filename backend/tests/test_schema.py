# The schema helper must work against databases created by older versions,
# including SQLite where ALTER TABLE cannot add a UNIQUE column directly.

from sqlalchemy import inspect, text

from extensions import db
from schema import ensure_resource_columns


def test_schema_upgrade_on_legacy_sqlite(app):
    with app.app_context():
        db.drop_all()

        db.session.execute(text("""
            CREATE TABLE resources (
                id INTEGER PRIMARY KEY,
                title VARCHAR(200),
                resource_type VARCHAR(50),
                file_path VARCHAR(500),
                is_published BOOLEAN,
                created_at DATETIME
            )
        """))
        db.session.commit()

        changes = ensure_resource_columns()

        assert "resources.slug" in changes
        assert "resources.external_url" in changes
        assert "ix_resources_slug" in changes

        columns = {
            column["name"]
            for column in inspect(db.engine).get_columns("resources")
        }
        indexes = {
            index["name"]
            for index in inspect(db.engine).get_indexes("resources")
        }

        assert "slug" in columns
        assert "external_url" in columns
        assert "ix_resources_slug" in indexes
        assert "ix_resources_catalogue" in indexes

        # Running it twice must be a no-op.
        assert ensure_resource_columns() == []
