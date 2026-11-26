# Replace generated SVG covers with real public-domain book images.
#
#   ../.venv/Scripts/python.exe tools/fetch_public_domain_covers.py
#
# Sources are tried in order: Open Library work covers, the Internet Archive
# item attached to the catalogue row, Gutenberg's cover CDN mirror, Open Library
# search, and finally an Internet Archive title search. Only English works
# first published by 1929 are accepted. Generated SVG covers, Open Library
# placeholder thumbnails and low-resolution scans are retried. Books with no
# suitable scan keep their existing fallback. Re-running skips real covers.

import argparse
import http.client
import json
import re
import ssl
import sys
import threading
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from difflib import SequenceMatcher
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from remote_covers import COVER_DIR  # noqa: E402

SEARCH = "https://openlibrary.org/search.json"
WORKS = "https://openlibrary.org/works"
COVERS = "https://covers.openlibrary.org/b/id"
GUTENBERG = "https://www.gutenberg.org/cache/epub"
GUTENBERG_MIRROR = "https://gutenberg.pglaf.org/cache/epub"
ARCHIVE_SEARCH = "https://archive.org/advancedsearch.php"
ARCHIVE_IMAGE = "https://archive.org/services/img"
ARCHIVE_DOWNLOAD = "https://archive.org/download"

CATALOGUES = [
    BASE_DIR / "catalogue" / "remote_books.json",
    BASE_DIR / "catalogue" / "fantasy_books.json",
    BASE_DIR / "catalogue" / "subject_books.json"
]
CUTOFF_YEAR = 1929
USER_AGENT = "E-Library-Cover-Fetcher/2.0"
MIN_COVER_BYTES = 3000
MIN_COVER_WIDTH = 150
MIN_COVER_HEIGHT = 200


_local = threading.local()


def get_connection(host, timeout):
    cache = getattr(_local, "connections", None)

    if cache is None:
        cache = {}
        _local.connections = cache

    connection = cache.get(host)

    if connection is None:
        connection = http.client.HTTPSConnection(
            host,
            timeout=timeout,
            context=ssl.create_default_context()
        )
        cache[host] = connection
    else:
        connection.timeout = timeout

    return connection


def drop_connection(host):
    cache = getattr(_local, "connections", {})
    connection = cache.pop(host, None)

    if connection is not None:
        try:
            connection.close()
        except Exception:
            pass


def fetch_bytes(url, timeout=30, attempts=3):
    for attempt in range(attempts):
        current = url

        for _ in range(5):
            parts = urllib.parse.urlsplit(current)
            host = parts.netloc
            path = parts.path or "/"

            if parts.query:
                path = f"{path}?{parts.query}"

            try:
                connection = get_connection(host, timeout)
                connection.request(
                    "GET",
                    path,
                    headers={
                        "User-Agent": USER_AGENT,
                        "Connection": "keep-alive"
                    }
                )
                response = connection.getresponse()
                data = response.read()

                if response.status in (301, 302, 303, 307, 308):
                    location = response.getheader("location")

                    if not location:
                        return None

                    current = urllib.parse.urljoin(current, location)
                    continue

                if response.status >= 400:
                    if response.status in (404, 410):
                        return None

                    drop_connection(host)
                    break

                return data
            except Exception:
                drop_connection(host)
                break

        if attempt == attempts - 1:
            return None

        time.sleep(0.5 + attempt)

    return None


def fetch_json(url, timeout=30, attempts=3):
    data = fetch_bytes(url, timeout=timeout, attempts=attempts)

    if not data:
        return None

    try:
        return json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None


def jpeg_size(data):
    """Return (width, height) from a JPEG without extra dependencies."""
    if not data or data[:2] != b"\xff\xd8":
        return None

    index = 2

    while index < len(data) - 9:
        if data[index] != 0xFF:
            index += 1
            continue

        marker = data[index + 1]
        index += 2

        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
            continue

        if marker == 0xDA:
            break

        length = int.from_bytes(data[index:index + 2], "big")

        if (
            0xC0 <= marker <= 0xCF
            and marker not in (0xC4, 0xC8, 0xCC)
        ):
            height = int.from_bytes(data[index + 3:index + 5], "big")
            width = int.from_bytes(data[index + 5:index + 7], "big")
            return width, height

        index += length

    return None


def is_real_cover(data):
    if not data or data[:3] != b"\xff\xd8\xff":
        return False

    if len(data) < MIN_COVER_BYTES:
        return False

    size = jpeg_size(data)

    return bool(
        size
        and size[0] >= MIN_COVER_WIDTH
        and size[1] >= MIN_COVER_HEIGHT
    )


def save_cover(book, data):
    path = COVER_DIR / f"{book['slug']}.jpg"
    path.write_bytes(data)
    return f"covers/{book['slug']}.jpg"


def cover_state(book):
    """Classify the current cover so placeholders and SVG fallbacks are retried."""
    cover = book.get("cover_image", "")

    if not cover:
        return "missing"

    if cover.lower().endswith(".svg"):
        return "generated"

    if not cover.lower().endswith((".jpg", ".jpeg")):
        return "other"

    path = COVER_DIR / Path(cover).name

    if not path.is_file():
        return "missing"

    data = path.read_bytes()

    if not data.startswith(b"\xff\xd8\xff"):
        return "invalid"

    size = jpeg_size(data)

    if not size:
        return "invalid"

    if size[0] < 80 or size[1] < 120 or len(data) < 1500:
        return "placeholder"

    if size[0] < MIN_COVER_WIDTH or size[1] < MIN_COVER_HEIGHT:
        return "lowres"

    return "real"


def normalise(value):
    return re.sub(r"[^a-z0-9]+", " ", (value or "").lower()).strip()


def similarity(wanted, candidate):
    wanted = normalise(wanted)
    candidate = normalise(candidate)

    if not wanted or not candidate:
        return 0.0

    if wanted == candidate:
        return 1.0

    if wanted in candidate:
        return 0.9

    wanted_tokens = " ".join(sorted(wanted.split()))
    candidate_tokens = " ".join(sorted(candidate.split()))

    if wanted_tokens in candidate_tokens:
        return 0.9

    return SequenceMatcher(None, wanted, candidate).ratio()


def first_author(book):
    return (book.get("author") or "").split(" & ")[0]


def english_or_unknown(value):
    if not value:
        return True

    if isinstance(value, (list, tuple)):
        value = " ".join(str(item) for item in value)

    value = str(value).lower()

    return "eng" in value or "english" in value


def fetch_work_cover_ids(work_key):
    olid = str(work_key or "").rstrip("/").split("/")[-1]

    if not re.fullmatch(r"OL\d+W", olid, re.IGNORECASE):
        return []

    work = fetch_json(f"{WORKS}/{olid}.json") or {}
    cover_ids = list(work.get("covers") or [])

    if not cover_ids:
        editions = fetch_json(
            f"{WORKS}/{olid}/editions.json?limit=10"
        ) or {}

        for edition in editions.get("entries", []):
            for cover_id in edition.get("covers") or []:
                if cover_id not in cover_ids:
                    cover_ids.append(cover_id)

    return cover_ids[:8]


def cover_from_open_library_ids(book, cover_ids):
    for cover_id in cover_ids:
        for size in ("L", "M"):
            data = fetch_bytes(
                f"{COVERS}/{cover_id}-{size}.jpg?default=false",
                attempts=2
            )

            if is_real_cover(data):
                return save_cover(book, data)

    return None


def cover_from_work(book):
    cover_ids = fetch_work_cover_ids(book.get("work_key"))

    if not cover_ids:
        return None

    return cover_from_open_library_ids(book, cover_ids)


def cover_from_archive_id(book):
    archive_id = book.get("archive_id")

    if not archive_id:
        return None

    urls = [
        f"{ARCHIVE_IMAGE}/{archive_id}",
        f"{ARCHIVE_DOWNLOAD}/{archive_id}/page/n0_w1000.jpg",
        f"{ARCHIVE_DOWNLOAD}/{archive_id}/page/n1_w1000.jpg"
    ]

    for url in urls:
        data = fetch_bytes(url, timeout=35, attempts=2)

        if is_real_cover(data):
            return save_cover(book, data)

    return None


def cover_from_gutenberg(book):
    gutenberg_id = book.get("gutenberg_id")

    if not gutenberg_id:
        return None

    for base in (GUTENBERG_MIRROR, GUTENBERG):
        data = fetch_bytes(
            f"{base}/{gutenberg_id}/pg{gutenberg_id}.cover.medium.jpg",
            attempts=2
        )

        if is_real_cover(data):
            return save_cover(book, data)

    return None


def open_library_candidate(book):
    title = book.get("title", "")
    author = first_author(book)
    queries = [f"{title} {author}"]

    if len(title) > 55:
        queries.append(title[:55])

    wanted = normalise(title)
    wanted_author = normalise(author)

    for query in queries:
        params = {
            "q": query,
            "public_scan_b": "true",
            "fields": (
                "key,title,author_name,first_publish_year,language,"
                "cover_i,public_scan_b"
            ),
            "limit": 10
        }
        url = SEARCH + "?" + urllib.parse.urlencode(params)
        docs = (fetch_json(url) or {}).get("docs", [])
        best = None
        best_score = 0.0

        for doc in docs:
            year = doc.get("first_publish_year") or 9999

            if year > CUTOFF_YEAR or not doc.get("cover_i"):
                continue

            if not english_or_unknown(doc.get("language")):
                continue

            title_score = similarity(wanted, doc.get("title"))

            names = doc.get("author_name", [])
            author_score = max(
                (similarity(wanted_author, name) for name in names),
                default=0
            )
            score = title_score * 0.7 + author_score * 0.3

            if score > best_score:
                best_score = score
                best = doc

        if best and best_score >= 0.62:
            return best

    return None


def cover_from_open_library_search(book):
    doc = open_library_candidate(book)

    if not doc:
        return None

    cover_ids = [doc["cover_i"]]
    cover_ids.extend(fetch_work_cover_ids(doc.get("key")))

    return cover_from_open_library_ids(book, cover_ids)


def archive_candidates(book):
    full_title = re.sub(
        r"[\"\\]", " ", book.get("title", "")
    )[:110].strip()

    if not full_title:
        return []

    short_title = re.split(
        r"\s*[:;—–,]\s+", full_title, maxsplit=1
    )[0][:70].strip()
    titles = [full_title]

    if short_title and short_title != full_title:
        titles.append(short_title)

    author = first_author(book)
    wanted_titles = [
        value for value in (
            normalise(book.get("title")),
            normalise(short_title)
        ) if value
    ]
    wanted_author = normalise(author)
    all_docs = []

    for title in titles:
        query = (
            f'title:("{title}") AND mediatype:texts '
            f'AND year:[* TO {CUTOFF_YEAR}]'
        )
        params = {
            "q": query,
            "fl[]": [
                "identifier", "title", "creator", "year", "language"
            ],
            "rows": 10,
            "output": "json"
        }
        url = ARCHIVE_SEARCH + "?" + urllib.parse.urlencode(
            params, doseq=True
        )
        docs = (
            (fetch_json(url) or {}).get("response") or {}
        ).get("docs", [])

        if not docs and author and author != "Unknown author":
            author_query = (
                f'title:("{title}") AND creator:("{author}") '
                f'AND mediatype:texts AND year:[* TO {CUTOFF_YEAR}]'
            )
            params["q"] = author_query
            url = ARCHIVE_SEARCH + "?" + urllib.parse.urlencode(
                params, doseq=True
            )
            docs = (
                (fetch_json(url) or {}).get("response") or {}
            ).get("docs", [])

        all_docs.extend(docs)

    scored = []

    for doc in all_docs:
        identifier = doc.get("identifier")

        if not identifier:
            continue

        if not english_or_unknown(doc.get("language")):
            continue

        candidate = doc.get("title") or ""

        if isinstance(candidate, list):
            candidate = candidate[0] if candidate else ""

        title_score = max(
            similarity(value, candidate) for value in wanted_titles
        )
        creator = doc.get("creator") or ""

        if isinstance(creator, list):
            creator = " ".join(str(item) for item in creator)

        author_score = 0.0

        if wanted_author and author != "Unknown author":
            author_score = similarity(wanted_author, creator)

        score = title_score * 0.8 + author_score * 0.2
        year = doc.get("year") or 0

        if score >= 0.55:
            scored.append((score, -int(year or 0), identifier))

    seen = set()
    ordered = []

    for score, negative_year, identifier in sorted(
        scored,
        reverse=True
    ):
        if identifier in seen:
            continue

        seen.add(identifier)
        ordered.append(identifier)

        if len(ordered) >= 5:
            break

    return ordered


def cover_from_archive_search(book):
    for identifier in archive_candidates(book):
        urls = [
            f"{ARCHIVE_IMAGE}/{identifier}",
            f"{ARCHIVE_DOWNLOAD}/{identifier}/page/n0_w1000.jpg",
            f"{ARCHIVE_DOWNLOAD}/{identifier}/page/n1_w1000.jpg"
        ]

        for url in urls:
            data = fetch_bytes(url, timeout=35, attempts=2)

            if is_real_cover(data):
                return save_cover(book, data)

    return None


def enrich(book):
    cover = book.get("cover_image", "")
    state = cover_state(book)

    if state == "real" or cover.startswith(("http:", "https:")):
        return book, "kept", "existing"

    strategies = []

    if book.get("work_key"):
        strategies.append(("Open Library work", cover_from_work))

    if book.get("archive_id"):
        strategies.append(("Internet Archive item", cover_from_archive_id))

    if book.get("gutenberg_id"):
        strategies.append(("Project Gutenberg", cover_from_gutenberg))

    strategies.extend([
        ("Open Library search", cover_from_open_library_search),
        ("Internet Archive search", cover_from_archive_search)
    ])

    for source, strategy in strategies:
        try:
            jpg = strategy(book)
        except Exception as error:
            print(
                f"  {book['slug']}: {source} failed: {error}",
                flush=True
            )
            continue

        if jpg:
            book["cover_image"] = jpg
            return book, "added", source

    return book, "kept", "no scan found"


def load_catalogues(names):
    if not names:
        return CATALOGUES

    wanted = {Path(name).name for name in names}
    return [path for path in CATALOGUES if path.name in wanted]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--catalog",
        action="append",
        help="limit the run to a catalogue filename (repeatable)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="only check the first N unsuitable covers in each catalogue"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=6,
        help="number of parallel cover lookups"
    )
    args = parser.parse_args()

    COVER_DIR.mkdir(parents=True, exist_ok=True)
    totals = {"added": 0, "kept": 0}

    for path in load_catalogues(args.catalog):
        if not path.is_file():
            continue

        data = json.loads(path.read_text(encoding="utf-8"))
        books = data.get("books", [])
        targets = [
            book for book in books
            if cover_state(book) != "real"
        ]

        if args.limit:
            targets = targets[:args.limit]

        sources = {}

        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = {
                pool.submit(enrich, book): book
                for book in targets
            }

            for future in as_completed(futures):
                book = futures[future]

                try:
                    _, outcome, source = future.result()
                except Exception as error:
                    outcome, source = "kept", f"error: {error}"

                totals[outcome] += 1
                sources[source] = sources.get(source, 0) + 1

        path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8"
        )

        states = {}

        for book in books:
            state = cover_state(book)
            states[state] = states.get(state, 0) + 1

        real = states.pop("real", 0)
        details = ", ".join(
            f"{count} {state}" for state, count in sorted(states.items())
        )
        print(f"{path.name}: {real}/{len(books)} real book images")

        if details:
            print(f"  remaining: {details}")

        for source, count in sorted(sources.items()):
            print(f"  {source}: {count}")

    print(
        f"Checked {totals['added'] + totals['kept']} unsuitable covers: "
        f"replaced {totals['added']}, kept {totals['kept']}."
    )


if __name__ == "__main__":
    main()
