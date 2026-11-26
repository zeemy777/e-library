# Allowlist for book links that stream from an external public-domain source.
#
# Admin-entered links are turned into 302 redirects by the reading endpoint,
# so only known hosts are accepted. This keeps members on the library's
# trusted reading destinations even when a catalogue row is edited by hand.

from urllib.parse import urlparse

ALLOWED_EXTERNAL_HOSTS = {
    "gutenberg.org",
    "www.gutenberg.org",
    "openlibrary.org",
    "www.openlibrary.org",
    "archive.org",
    "www.archive.org"
}


def is_allowed_external_url(value):
    """Return True for a plain https URL on an approved host."""

    if not value or not isinstance(value, str):
        return False

    try:
        parsed = urlparse(value.strip())
    except ValueError:
        return False

    host = (parsed.hostname or "").lower().rstrip(".")

    return (
        parsed.scheme == "https"
        and host in ALLOWED_EXTERNAL_HOSTS
        and parsed.username is None
        and parsed.password is None
    )
