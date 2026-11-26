# Small, idempotent schema upgrades for databases created by older versions.
#
# The project uses db.create_all() rather than a migration framework, so new
# columns are not added to an existing MySQL table automatically. The seed
# script calls this helper before writing any catalogue rows.

from sqlalchemy import inspect, text

from extensions import db


def ensure_resource_columns():
    """Add catalogue columns missing from an existing resources table."""

    inspector = inspect(db.engine)
    tables = set(inspector.get_table_names())

    if "resources" not in tables:
        return []

    existing = {
        column["name"]
        for column in inspector.get_columns("resources")
    }

    changes = []

    index_names = {
        index["name"]
        for index in inspector.get_indexes("resources")
    }

    with db.engine.begin() as connection:
        if "slug" not in existing:
            # SQLite cannot add a UNIQUE column with ALTER TABLE. Adding a
            # unique index afterwards works on both SQLite and MySQL.
            connection.execute(text(
                "ALTER TABLE resources "
                "ADD COLUMN slug VARCHAR(100) NULL"
            ))
            changes.append("resources.slug")

        if "external_url" not in existing:
            connection.execute(text(
                "ALTER TABLE resources "
                "ADD COLUMN external_url VARCHAR(500) NULL"
            ))
            changes.append("resources.external_url")

        if "slug" not in existing and "ix_resources_slug" not in index_names:
            try:
                connection.execute(text(
                    "CREATE UNIQUE INDEX ix_resources_slug "
                    "ON resources (slug)"
                ))
                changes.append("ix_resources_slug")
            except Exception:
                # Legacy rows with duplicate empty slugs should not block
                # the rest of the upgrade.
                pass

        catalogue_columns = {
            "is_published", "resource_type", "created_at", "id"
        }

        if (
            "ix_resources_catalogue" not in index_names
            and catalogue_columns <= existing
        ):
            connection.execute(text(
                "CREATE INDEX ix_resources_catalogue "
                "ON resources (is_published, resource_type, created_at, id)"
            ))
            changes.append("ix_resources_catalogue")

    return changes
