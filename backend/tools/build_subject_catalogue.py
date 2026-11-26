# Expand the six non-fantasy shelves from public-domain scans indexed by
# Open Library.
#
#   ../.venv/Scripts/python.exe tools/build_subject_catalogue.py
#
# Only English works first published by 1929 that Open Library marks as having
# a public scan are accepted. Reading links point at the matching Internet
# Archive item, cover images are downloaded from Open Library's cover service,
# and the committed JSON is the offline source of truth used by seed_library.py.

import json
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from library_catalogue import BOOKS  # noqa: E402
from remote_covers import COVER_DIR, write_covers  # noqa: E402

SEARCH = "https://openlibrary.org/search.json"
COVERS = "https://covers.openlibrary.org/b/id"
OUTPUT = BASE_DIR / "catalogue" / "subject_books.json"
SOURCES = [
    BASE_DIR / "catalogue" / "remote_books.json",
    BASE_DIR / "catalogue" / "fantasy_books.json"
]
CUTOFF_YEAR = 1929
MAX_PER_CATEGORY = 500
MAX_PAGES_PER_QUERY = 6
SEARCH_WORKERS = 6
COVER_WORKERS = 12
USER_AGENT = "E-Library-Subject-Catalogue/1.0"

# Broad subject queries overlap, so a work is kept for the first category
# whose vocabulary describes it best. Four high-yield queries per shelf keep
# the crawl practical; the cap leaves room for every eligible work found while
# keeping the committed cover set a reasonable size.
QUERIES = {
    "Business": ["business", "economics", "finance", "commerce"],
    "History": [
        "history", "ancient history", "medieval history", "biography"
    ],
    "Literature": ["literature", "fiction", "poetry", "novels"],
    "Mathematics": ["mathematics", "algebra", "geometry", "calculus"],
    "Science": ["science", "physics", "chemistry", "biology"],
    "Technology": ["technology", "engineering", "electricity", "machinery"]
}

PATTERNS = {
    "Business": [
        r"\bbusiness", r"\beconom", r"\bfinanc", r"\bcommerc",
        r"\baccount", r"\bbanking", r"\binvest", r"\bmanagement",
        r"\bmarket", r"\btrade\b", r"\btax", r"\bcurrency", r"\binsuranc",
        r"\bcapital", r"\bprice", r"\bprofit", r"\bindustr"
    ],
    "History": [
        r"\bhistor", r"\bancient", r"\bmedieval", r"\bchronic",
        r"\barchaeolog", r"\bempire", r"\bcivilisation",
        r"\bcivilization", r"\brevolution", r"\bwar\b", r"\bwars\b",
        r"\bbiograph", r"\bmemoir", r"\bexplor", r"\bdynast", r"\bcentury"
    ],
    "Literature": [
        r"\bliterar", r"\bfiction", r"\bnovel", r"\bpoetr", r"\bpoems?\b",
        r"\bdrama", r"\bplays?\b", r"\bessays?", r"\bshort stor",
        r"\bauthors?", r"\bauthors\b", r"\bprose\b", r"\bcritics?\b"
    ],
    "Mathematics": [
        r"\bmathematic", r"\balgebra", r"\bgeometr", r"\bcalculus",
        r"\barithmet", r"\btrigonometr", r"\bstatistic", r"\bprobabilit",
        r"\blogarithm", r"\bnumbers?\b", r"\bmeasurement"
    ],
    "Science": [
        r"\bscience", r"\bscientific", r"\bphysic", r"\bchemistr",
        r"\bbiolo", r"\bbotan", r"\bzoolog", r"\bgeolog", r"\bastronom",
        r"\banatom", r"\bevolut", r"\bnatural history", r"\bheredity",
        r"\bgenetic", r"\bmedicine", r"\bmedical", r"\boptics?\b"
    ],
    "Technology": [
        r"\btechnolog", r"\bengineer", r"\belectric", r"\bmachiner",
        r"\bmanufactur", r"\brailway", r"\bsteam", r"\btelegraph",
        r"\btelephone", r"\bmechanic", r"\bindustr", r"\barchitecture",
        r"\bmining", r"\bships?\b", r"\bbridges?\b"
    ]
}

UNWANTED = [
    r"\bfinanc", r"\beconom", r"\baccount", r"\bmanufactur",
    r"\bengineering", r"\bmedicine", r"\bmedical", r"\blaw\b",
    r"\bcatalog", r"\bprice list"
]

COMPILED = {
    category: [re.compile(pattern) for pattern in patterns]
    for category, patterns in PATTERNS.items()
}
COMPILED_UNWANTED = [re.compile(pattern) for pattern in UNWANTED]


def request_json(url):
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT}
    )

    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=25) as response:
                return json.load(response)
        except Exception as error:
            if attempt == 2:
                print(f"  request failed: {error}", flush=True)
                return None
            time.sleep(attempt + 1)

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


def fetch_all_pages():
    """Fetch every query page concurrently but keep deterministic ordering."""
    jobs = [
        (category, query, page)
        for category, queries in QUERIES.items()
        for query in queries
        for page in range(1, MAX_PAGES_PER_QUERY + 1)
    ]
    pages = defaultdict(dict)
    completed = 0

    with ThreadPoolExecutor(max_workers=SEARCH_WORKERS) as pool:
        futures = {
            pool.submit(search_page, query, page): (category, query, page)
            for category, query, page in jobs
        }

        for future in as_completed(futures):
            category, query, page = futures[future]

            try:
                docs = future.result()
            except Exception as error:
                docs = []
                print(
                    f"  page failed: {category} / {query} p{page}: {error}",
                    flush=True
                )

            pages[(category, query)][page] = docs
            completed += 1

            if completed % 24 == 0:
                print(f"  fetched {completed}/{len(jobs)} pages", flush=True)

    return pages


def normalize(value):
    return re.sub(r"[^a-z0-9]+", "", (value or "").lower())


def clean(value):
    return re.sub(r"\s+\s", " ", str(value or "")).strip()


def shorten(value, limit=330):
    if len(value) <= limit:
        return value
    return value[:limit].rsplit(" ", 1)[0].rstrip(" ,;:") + "…"


def author_of(doc):
    names = [clean(name) for name in doc.get("author_name", [])]
    return " & ".join(name for name in names[:3] if name) or "Unknown author"


def title_hits(text, category):
    return sum(
        1 for pattern in COMPILED[category] if pattern.search(text)
    )


def relevant(doc, category):
    title = clean(doc.get("title")).lower()
    subjects = " ".join(
        clean(subject) for subject in doc.get("subject", [])
    ).lower()

    own_title = title_hits(title, category)
    own_subjects = title_hits(subjects, category)

    if own_title == 0 and own_subjects < 2:
        return False

    # If another shelf's vocabulary clearly wins in the title, let that
    # query claim the book instead of filing it under the current category.
    other_best = max(
        title_hits(title, other)
        for other in COMPILED if other != category
    )

    if other_best > own_title and own_subjects < 3:
        return False

    return True


def description_of(doc, category):
    subjects = []

    for raw in doc.get("subject", []):
        subject = clean(raw)

        if not subject or len(subject) > 90:
            continue

        if any(pattern.search(subject.lower()) for pattern in COMPILED_UNWANTED):
            continue

        if subject not in subjects:
            subjects.append(subject)

    # Put the most characteristic subjects first so each shelf reads clearly.
    subjects.sort(key=lambda subject: -title_hits(subject.lower(), category))
    summary = "; ".join(subjects[:4])
    summary = shorten(
        summary or f"A public-domain {category.lower()} work from the scanned collection.",
        300
    )

    return (
        f"{summary} Read the scanned edition free through the Internet Archive. "
        "No download is stored in this library."
    )


def existing_identity():
    titles = {normalize(book["title"]) for book in BOOKS}
    slugs = {book["slug"] for book in BOOKS}

    for path in SOURCES:
        if not path.is_file():
            continue

        data = json.loads(path.read_text(encoding="utf-8"))

        for book in data.get("books", []):
            titles.add(normalize(book["title"]))
            slugs.add(book["slug"])

    return titles, slugs


def download_cover(book):
    slug = book["slug"]
    path = COVER_DIR / f"{slug}.jpg"
    cover_id = book.pop("cover_id", None)

    if not cover_id:
        return None

    url = f"{COVERS}/{cover_id}-S.jpg"

    for attempt in range(2):
        try:
            request = urllib.request.Request(
                url,
                headers={"User-Agent": USER_AGENT}
            )

            with urllib.request.urlopen(request, timeout=20) as response:
                data = response.read()

            if data[:3] == b"\xff\xd8\xff" and len(data) > 1000:
                path.write_bytes(data)
                return f"covers/{slug}.jpg"
            break
        except Exception:
            if attempt == 1:
                break
            time.sleep(1)

    return None


def add_fallback_cover(book):
    """Create a local SVG cover immediately so the catalogue is usable."""
    digits = re.sub(r"\D", "", book["slug"])[-6:]
    book["gutenberg_id"] = int(digits or 0)
    book["source_label"] = "OPEN LIBRARY"
    write_covers([book])
    book.pop("gutenberg_id", None)
    book.pop("source_label", None)


def write_output(books):
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(
            {
                "source": (
                    "Open Library / Internet Archive public-domain scans for "
                    "Business, History, Literature, Mathematics, Science and "
                    "Technology (works first published by 1929)"
                ),
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "count": len(books),
                "books": books
            },
            indent=2,
            ensure_ascii=False
        ) + "\n",
        encoding="utf-8"
    )


def upgrade_covers(books):
    """Replace SVG fallbacks with real Open Library scans where possible."""
    upgraded = 0

    with ThreadPoolExecutor(max_workers=COVER_WORKERS) as pool:
        futures = {
            pool.submit(download_cover, book): book
            for book in books
        }

        for future in as_completed(futures):
            book = futures[future]

            try:
                jpg = future.result()
            except Exception as error:
                jpg = None
                print(
                    f"  cover failed for {book['slug']}: {error}",
                    flush=True
                )

            if jpg:
                book["cover_image"] = jpg
                upgraded += 1

    print(f"  upgraded {upgraded} covers to real scans", flush=True)


def covers_only():
    """Resume just the cover phase after an interrupted crawl."""
    data = json.loads(OUTPUT.read_text(encoding="utf-8"))
    books = data["books"]

    for book in books:
        if not book.get("cover_image"):
            add_fallback_cover(book)

    upgrade_covers(books)
    write_output(books)

    for category in QUERIES:
        category_books = [
            book for book in books if book["category"] == category
        ]
        real = sum(
            book["cover_image"].endswith(".jpg")
            for book in category_books
        )
        print(
            f"  {category:11} {len(category_books):4} books, "
            f"{real:4} real scans"
        )


def main():
    COVER_DIR.mkdir(parents=True, exist_ok=True)
    titles, slugs = existing_identity()
    seen_keys = set()
    seen_titles = set(titles)
    candidates = defaultdict(list)

    pages = fetch_all_pages()

    for category, queries in QUERIES.items():
        for query in queries:
            for page in range(1, MAX_PAGES_PER_QUERY + 1):
                docs = pages.get((category, query), {}).get(page, [])

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

                    if identity in seen_titles:
                        continue

                    if not relevant(doc, category):
                        continue

                    seen_titles.add(identity)
                    work_id = key.rstrip("/").split("/")[-1]
                    slug = f"ol-{work_id.lower()}"

                    if slug in slugs:
                        continue

                    slugs.add(slug)
                    archive_id = doc["ia"][0]

                    candidates[category].append({
                        "slug": slug,
                        "title": shorten(title, 195),
                        "author": author_of(doc),
                        "publisher": "Open Library / Internet Archive",
                        "category": category,
                        "description": description_of(doc, category),
                        "source": "remote",
                        "work_key": key,
                        "archive_id": archive_id,
                        "cover_id": doc["cover_i"],
                        "first_published": year,
                        "external_url": (
                            "https://archive.org/details/"
                            f"{urllib.parse.quote(archive_id, safe='')}"
                        )
                    })

                if len(candidates[category]) >= MAX_PER_CATEGORY:
                    break

            if len(candidates[category]) >= MAX_PER_CATEGORY:
                break

    selected = []

    for category, books in candidates.items():
        category_books = sorted(
            books,
            key=lambda book: (book["first_published"], book["title"].lower())
        )[:MAX_PER_CATEGORY]
        selected.extend(category_books)

    # Checkpoint immediately: SVG fallbacks are instant, so even an interrupted
    # run leaves a complete, seedable catalogue. Real scans are added next.
    for book in selected:
        add_fallback_cover(book)

    write_output(selected)
    print(f"Checkpointed {len(selected)} subject books", flush=True)

    upgrade_covers(selected)
    write_output(selected)

    print(f"Wrote {len(selected)} subject books to {OUTPUT.name}")
    for category in QUERIES:
        books = [book for book in selected if book["category"] == category]
        real = sum(book["cover_image"].endswith(".jpg") for book in books)
        print(f"  {category:11} {len(books):4} books, {real:4} real scans")


if __name__ == "__main__":
    if "--covers-only" in sys.argv:
        covers_only()
    else:
        main()
