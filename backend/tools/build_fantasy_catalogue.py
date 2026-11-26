# Build the Fantasy shelf from public-domain scans indexed by Open Library.
#
#   ../.venv/Scripts/python.exe tools/build_fantasy_catalogue.py
#
# Only works published by 1929 that Open Library marks as having a public
# scan are accepted, and reading links point at the matching Internet Archive
# item. Cover images are downloaded from Open Library's cover service. The
# resulting JSON is committed, so seeding never needs network access.

import json
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from fetch_public_domain_covers import is_real_cover  # noqa: E402
from library_catalogue import BOOKS  # noqa: E402
from remote_covers import COVER_DIR, write_covers  # noqa: E402

SEARCH = "https://openlibrary.org/search.json"
COVERS = "https://covers.openlibrary.org/b/id"
OUTPUT = BASE_DIR / "catalogue" / "fantasy_books.json"
REMOTE = BASE_DIR / "catalogue" / "remote_books.json"
TARGET = 250
CUTOFF_YEAR = 1929
USER_AGENT = "E-Library-Fantasy-Catalogue/1.0"

# A few overlapping searches find old fairy tales, myths and marvelous
# romances that would not necessarily use the word "fantasy" themselves.
QUERIES = {
    "fantasy": 11,
    "fairy tale": 5,
    "legends": 4,
    "magic": 4,
    "wonder": 3,
    "dragon": 3,
    "wizard": 3,
    "myth": 3,
    "enchant": 3,
    "goblin": 2,
    "giant": 2,
    "faerie": 2
}

STRONG = [
    r"\bfantas", r"\bfairy", r"\bfaerie", r"\bmagic", r"\benchant",
    r"\bdragon", r"\bwizard", r"\bsorcer", r"\bwitch", r"\bgoblin",
    r"\bgnome", r"\bgiant", r"\belves\b", r"\belf\b", r"\bmermaid",
    r"\bogre", r"\btroll", r"\bmyth", r"\blegend", r"\bmarvel",
    r"\bother ?world", r"\boccult", r"\bphantom", r"\bspirit",
    r"\bgenie", r"\balchem", r"\bgiant"
]
WEAK = [
    r"\bromance", r"\badventur", r"\bdream", r"\bvision", r"\bstrange",
    r"\bmyster", r"\bcurse", r"\bcharm", r"\bghost", r"\bhorror",
    r"\bheroic", r"\bwonder", r"\bimpossible", r"\benchanted"
]
UNWANTED = [
    r"\bfinanc", r"\beconom", r"\baccount", r"\bmanufactur",
    r"\bengineering", r"\bmedicine", r"\bmedical", r"\blaw\b",
    r"\bpolitical", r"\bbiograph", r"\bsermon", r"\btextbook",
    r"\bcatalog", r"\bprice list"
]
# "Fantasy" is also a music term and a subject tag on some non-fiction.
# Title checks catch musical form and psychology books; subject checks catch
# memoirs and scores that happen to use the word "fantasy".
EXCLUDED_TITLE = [
    r"\bpsycholog", r"\bfantasia\b", r"\bfantasie\b", r"\bfugues?",
    r"\bmusical fantas"
]
EXCLUDED_SUBJECT = [
    r"\bpsychoanalys", r"\bautobiograph", r"\bmemoir", r"\bpiano music",
    r"\bcanons and fugues", r"\borchestra", r"\bmusical fantas"
]
KNOWN_AUTHORS = {
    "l. frank baum", "george macdonald", "edith nesbit",
    "william morris", "lord dunsany", "algernon blackwood",
    "a. merritt", "david lindsay", "h. rider haggard",
    "arthur machen", "rudyard kipling", "j. m. barrie",
    "washington irving", "sheridan le fanu", "bram stoker",
    "mary shelley", "edgar allan poe", "h. g. wells",
    "andrew lang", "charles kingsley", "george sand",
    "james Stephens".lower()
}

COMPILED_STRONG = [re.compile(pattern) for pattern in STRONG]
COMPILED_WEAK = [re.compile(pattern) for pattern in WEAK]
COMPILED_UNWANTED = [re.compile(pattern) for pattern in UNWANTED]
COMPILED_EXCLUDED_TITLE = [
    re.compile(pattern) for pattern in EXCLUDED_TITLE
]
COMPILED_EXCLUDED_SUBJECT = [
    re.compile(pattern) for pattern in EXCLUDED_SUBJECT
]


def request_json(url):
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT}
    )

    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=40) as response:
                return json.load(response)
        except Exception as error:
            if attempt == 2:
                print(f"  request failed: {error}", flush=True)
                return None
            time.sleep(1.5 * (attempt + 1))

    return None


def search_page(query, page):
    params = {
        "q": query,
        "public_scan_b": "true",
        "fields": (
            "key,title,author_name,first_publish_year,language,ia,"
            "public_scan_b,cover_i,subject"
        ),
        "limit": 100,
        "offset": (page - 1) * 100
    }
    url = SEARCH + "?" + urllib.parse.urlencode(params)
    data = request_json(url)
    return (data or {}).get("docs", [])


def normalize(value):
    return re.sub(r"[^a-z0-9]+", "", (value or "").lower())


def clean(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()


def shorten(value, limit=330):
    if len(value) <= limit:
        return value
    return value[:limit].rsplit(" ", 1)[0].rstrip(" ,;:") + "…"


def author_of(doc):
    names = [clean(name) for name in doc.get("author_name", [])]
    return " & ".join(name for name in names[:3] if name) or "Unknown author"


def relevant(doc):
    title = clean(doc.get("title"))
    subjects = " ".join(clean(subject) for subject in doc.get("subject", []))
    author = author_of(doc).lower()

    if any(pattern.search(title.lower()) for pattern in COMPILED_UNWANTED):
        return False

    if any(pattern.search(title.lower()) for pattern in COMPILED_EXCLUDED_TITLE):
        return False

    if any(
        pattern.search(subjects.lower())
        for pattern in COMPILED_EXCLUDED_SUBJECT
    ):
        return False

    score = 0
    score += 4 * sum(
        1 for pattern in COMPILED_STRONG if pattern.search(title.lower())
    )
    score += 2 * sum(
        1 for pattern in COMPILED_STRONG if pattern.search(subjects.lower())
    )
    score += 1 * sum(
        1 for pattern in COMPILED_WEAK if pattern.search(title.lower())
    )
    score += 1 * sum(
        1 for pattern in COMPILED_WEAK if pattern.search(subjects.lower())
    )

    if any(name in author for name in KNOWN_AUTHORS):
        score += 4

    return score >= 4


def description_of(doc):
    subjects = []

    for raw in doc.get("subject", []):
        subject = clean(raw)

        if not subject or len(subject) > 90:
            continue

        if any(pattern.search(subject.lower()) for pattern in COMPILED_UNWANTED):
            continue

        if subject not in subjects:
            subjects.append(subject)

    summary = "; ".join(subjects[:4])
    summary = shorten(
        summary or "An imaginative public-domain story for readers of all ages.",
        300
    )

    return (
        f"{summary} Read the scanned edition free through the Internet Archive. "
        "No download is stored in this library."
    )


def cover_path(slug, cover_id):
    COVER_DIR.mkdir(parents=True, exist_ok=True)
    path = COVER_DIR / f"{slug}.jpg"
    url = f"{COVERS}/{cover_id}-L.jpg"

    for attempt in range(3):
        try:
            request = urllib.request.Request(
                url,
                headers={"User-Agent": USER_AGENT}
            )

            with urllib.request.urlopen(request, timeout=30) as response:
                data = response.read()

            if is_real_cover(data):
                path.write_bytes(data)
                return f"covers/{slug}.jpg"
            break
        except Exception:
            if attempt == 2:
                break
            time.sleep(1 + attempt)

    return None


def existing_identity():
    titles = {normalize(book["title"]) for book in BOOKS}
    keys = set()

    if REMOTE.is_file():
        data = json.loads(REMOTE.read_text(encoding="utf-8"))
        titles.update(
            normalize(book["title"]) for book in data.get("books", [])
        )

    return titles, keys


def main():
    titles, _ = existing_identity()
    candidates = {}
    seen_keys = set()
    seen_titles = set()

    for query, pages in QUERIES.items():
        for page in range(1, pages + 1):
            docs = search_page(query, page)
            print(f"{query} p{page}: {len(docs)} results", flush=True)

            for doc in docs:
                key = doc.get("key")

                if not key or key in seen_keys:
                    continue

                seen_keys.add(key)

                year = doc.get("first_publish_year") or 9999
                title = clean(doc.get("title"))

                if year > CUTOFF_YEAR or not title:
                    continue

                if "eng" not in (doc.get("language") or []):
                    continue

                if not doc.get("public_scan_b"):
                    continue

                if not doc.get("cover_i") or not doc.get("ia"):
                    continue

                identity = normalize(title)

                if identity in titles or identity in seen_titles:
                    continue

                if not relevant(doc):
                    continue

                seen_titles.add(identity)
                work_id = key.rstrip("/").split("/")[-1]
                slug = f"ol-{work_id.lower()}"

                candidates[slug] = {
                    "slug": slug,
                    "title": shorten(title, 195),
                    "author": author_of(doc),
                    "publisher": "Open Library / Internet Archive",
                    "category": "Fantasy",
                    "description": description_of(doc),
                    "source": "remote",
                    "work_key": key,
                    "archive_id": doc["ia"][0],
                    "cover_id": doc["cover_i"],
                    "first_published": year,
                    "external_url": (
                        "https://archive.org/details/"
                        f"{urllib.parse.quote(doc['ia'][0], safe='')}"
                    )
                }

            if len(candidates) >= TARGET:
                break

        if len(candidates) >= TARGET:
            break

    selected = sorted(
        candidates.values(),
        key=lambda book: (book["first_published"], book["title"].lower())
    )[:TARGET]

    for book in selected:
        cover = cover_path(book["slug"], book["cover_id"])

        if cover:
            book["cover_image"] = cover
        else:
            # Keep the typographic cover as a fallback if Open Library's
            # image service is unavailable or returns something unusable.
            book["gutenberg_id"] = int(
                re.sub(r"\D", "", book["slug"])[-6:] or 0
            )
            write_covers([book])
            book.pop("gutenberg_id", None)

        book.pop("cover_id", None)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(
            {
                "source": (
                    "Open Library / Internet Archive public-domain fantasy "
                    "scans (works first published by 1929)"
                ),
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "count": len(selected),
                "books": selected
            },
            indent=2,
            ensure_ascii=False
        ) + "\n",
        encoding="utf-8"
    )

    print(f"Wrote {len(selected)} fantasy books to {OUTPUT.name}")
    print(f"  Real cover scans: {Counter('jpg' in b['cover_image'] for b in selected)[True]}")
    print(f"  Typographic fallbacks: {Counter('svg' in b['cover_image'] for b in selected)[True]}")


if __name__ == "__main__":
    main()
