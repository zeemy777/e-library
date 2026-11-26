# Replace generated SVG covers with real public-domain scan covers.
#
#   ../.venv/Scripts/python.exe tools/fetch_public_domain_covers.py
#
# Open Library indexes scanned editions from the Internet Archive. This tool
# only accepts English works first published by 1929 that Open Library marks
# as having a public scan. Books with no suitable scan keep their SVG cover.
# Re-running skips rows that already have a JPEG cover.

import json
import re
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from difflib import SequenceMatcher
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from remote_covers import COVER_DIR  # noqa: E402

SEARCH = "https://openlibrary.org/search.json"
COVERS = "https://covers.openlibrary.org/b/id"
ARCHIVE_SEARCH = "https://archive.org/advancedsearch.php"
ARCHIVE_IMAGE = "https://archive.org/services/img"
CATALOGUES = [
    BASE_DIR / "catalogue" / "remote_books.json",
    BASE_DIR / "catalogue" / "fantasy_books.json"
]
CUTOFF_YEAR = 1929
USER_AGENT = "E-Library-Cover-Fetcher/1.0"


def request_json(url):
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT}
    )

    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=35) as response:
                return json.load(response)
        except Exception:
            if attempt == 2:
                return None
            time.sleep(1 + attempt)

    return None


def normalize(value):
    return re.sub(r"[^a-z0-9]+", " ", (value or "").lower()).strip()


def search_cover(book):
    title = book.get("title", "")
    author = book.get("author", "").split(" & ")[0]

    queries = [f"{title} {author}"]

    if len(title) > 55:
        queries.append(title[:55])

    wanted = normalize(title)
    wanted_author = normalize(author)

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
        data = request_json(url)
        docs = (data or {}).get("docs", [])
        best = None
        best_score = 0

        for doc in docs:
            year = doc.get("first_publish_year") or 9999

            if year > CUTOFF_YEAR or not doc.get("cover_i"):
                continue

            if "eng" not in (doc.get("language") or []):
                continue

            candidate = normalize(doc.get("title"))
            title_score = SequenceMatcher(
                None, wanted, candidate
            ).ratio()

            names = [normalize(name) for name in doc.get("author_name", [])]
            author_score = max(
                (SequenceMatcher(None, wanted_author, name).ratio()
                 for name in names),
                default=0
            )

            score = title_score * 0.7 + author_score * 0.3

            if score > best_score:
                best_score = score
                best = doc

        if best and best_score >= 0.62:
            return best

    return None


def archive_cover(book):
    # Open Library does not have a cover id for every old Gutenberg text.
    # The Internet Archive often has a scanned edition with a usable cover.
    full_title = re.sub(r"[\"\\]", " ", book.get("title", ""))[:100].strip()

    if not full_title:
        return None

    short_title = re.split(
        r"\s*[:;—–,]\s+", full_title, maxsplit=1
    )[0][:70].strip()
    queries = [full_title]

    if short_title and short_title != full_title:
        queries.append(short_title)

    wanted = [normalize(book.get("title")), normalize(short_title)]

    for query in queries:
        params = {
            "q": f'title:("{query}") AND mediatype:texts AND year:[* TO 1929]',
            "fl[]": ["identifier", "title", "creator", "year", "language"],
            "rows": 10,
            "output": "json"
        }
        url = ARCHIVE_SEARCH + "?" + urllib.parse.urlencode(params, doseq=True)
        docs = ((request_json(url) or {}).get("response") or {}).get("docs", [])
        best = None
        best_score = 0

        for doc in docs:
            language = doc.get("language") or ""

            if isinstance(language, list):
                language = " ".join(language)

            language = str(language).lower()

            if "eng" not in language and "english" not in language:
                continue

            candidate = doc.get("title") or ""

            if isinstance(candidate, list):
                candidate = candidate[0] if candidate else ""

            candidate = normalize(candidate)
            score = max(
                SequenceMatcher(None, value, candidate).ratio()
                for value in wanted if value
            )

            if score > best_score and doc.get("identifier"):
                best_score = score
                best = doc

        if not best or best_score < 0.55:
            continue

        slug = book["slug"]
        path = COVER_DIR / f"{slug}.jpg"
        url = f"{ARCHIVE_IMAGE}/{best['identifier']}"

        for attempt in range(3):
            try:
                request = urllib.request.Request(
                    url,
                    headers={"User-Agent": USER_AGENT}
                )

                with urllib.request.urlopen(request, timeout=30) as response:
                    data = response.read()

                if data[:3] == b"\xff\xd8\xff" and len(data) > 1500:
                    path.write_bytes(data)
                    return f"covers/{slug}.jpg"
                break
            except Exception:
                if attempt == 2:
                    break
                time.sleep(1 + attempt)

    return None


def download_cover(book, doc):
    slug = book["slug"]
    path = COVER_DIR / f"{slug}.jpg"
    url = f"{COVERS}/{doc['cover_i']}-M.jpg"

    for attempt in range(3):
        try:
            request = urllib.request.Request(
                url,
                headers={"User-Agent": USER_AGENT}
            )

            with urllib.request.urlopen(request, timeout=30) as response:
                data = response.read()

            if data[:3] == b"\xff\xd8\xff" and len(data) > 2000:
                path.write_bytes(data)
                return f"covers/{slug}.jpg"
            break
        except Exception:
            if attempt == 2:
                break
            time.sleep(1 + attempt)

    return None


def enrich(book):
    cover = book.get("cover_image", "")

    if cover.endswith(".jpg") or cover.startswith(("http:", "https:")):
        return book, False

    doc = search_cover(book)

    if doc:
        jpg = download_cover(book, doc)

        if jpg:
            book["cover_image"] = jpg
            return book, True

    jpg = archive_cover(book)

    if jpg:
        book["cover_image"] = jpg
        return book, True

    return book, False


def main():
    COVER_DIR.mkdir(parents=True, exist_ok=True)
    totals = {"checked": 0, "added": 0, "kept": 0}

    for path in CATALOGUES:
        if not path.is_file():
            continue

        data = json.loads(path.read_text(encoding="utf-8"))
        books = data.get("books", [])
        targets = [
            book for book in books
            if not book.get("cover_image", "").endswith(".jpg")
        ]

        with ThreadPoolExecutor(max_workers=6) as pool:
            futures = [pool.submit(enrich, book) for book in targets]

            for future in as_completed(futures):
                _, added = future.result()
                totals["checked"] += 1
                totals["added" if added else "kept"] += 1

        path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8"
        )

        jpg_count = sum(
            1 for book in books
            if book.get("cover_image", "").endswith(".jpg")
        )
        print(
            f"{path.name}: {jpg_count}/{len(books)} real cover scans"
        )

    print(
        f"Checked {totals['checked']} generated covers: "
        f"replaced {totals['added']}, kept {totals['kept']}."
    )


if __name__ == "__main__":
    main()
