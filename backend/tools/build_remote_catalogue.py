# Generate the remote (streamed) part of the catalogue from Gutendex metadata.
#
#   ../.venv/Scripts/python.exe tools/build_remote_catalogue.py
#
# The output, backend/catalogue/remote_books.json, is committed to the repo, so
# running the seed script never needs network access. Re-run this tool only when
# you want to refresh or enlarge the remote collection.

import json
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from category_rules import CATEGORY_ORDER, classify  # noqa: E402
from library_catalogue import BOOKS  # noqa: E402
from remote_covers import write_covers  # noqa: E402

API = "https://gutendex.com/books/"
OUTPUT = BASE_DIR / "catalogue" / "remote_books.json"
TARGET = 300
PAGES = 10
PAGE_SIZE = 32
USER_AGENT = "E-Library-Catalogue-Builder/1.0"

# A small set of targeted searches adds non-fiction candidates to the
# popularity list. Fewer calls keep refreshes quick and polite to the API.
TOPIC_QUERIES = [
    "computer",
    "engineering",
    "mathematics",
    "algebra",
    "economics",
    "management",
    "physics",
    "astronomy",
    "biology",
    "chemistry"
]


def fetch_page(page=1, search=None):
    params = {"page": page}

    if search:
        params["search"] = search

    url = f"{API}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT}
    )

    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=25) as response:
                return json.load(response).get("results", [])
        except Exception as error:
            if attempt == 2:
                print(
                    f"  fetch failed ({search or 'popular'} p{page}): {error}",
                    flush=True
                )
                return []
            time.sleep(1.5 * (attempt + 1))

    return []


def normalize_title(title):
    return re.sub(r"[^a-z0-9]+", "", title.lower())


def clean_text(value):
    # Gutenberg metadata uses "$b" as a subtitle separator.
    value = re.sub(r"\$b\s*", ": ", str(value or ""))
    value = re.sub(r"\s+", " ", value).strip()
    return value


def clean_summary(value):
    value = clean_text(value)
    value = re.sub(
        r"\s*\(This is an automatically generated summary\.?\)\s*$",
        "",
        value,
        flags=re.IGNORECASE
    )
    return value.strip()


def clean_author(value):
    value = clean_text(value)
    value = re.sub(r"\s*\(\d{4}[^)]*\)\s*$", "", value)

    if "," in value:
        last, first = value.split(",", 1)
        value = f"{first.strip()} {last.strip()}".strip()

    return value or "Unknown author"


def shorten(value, limit):
    if len(value) <= limit:
        return value
    clipped = value[:limit].rsplit(" ", 1)[0].rstrip(" ,;:")
    return clipped + "…"


def guess_category(item):
    title = clean_text(item.get("title"))
    subjects = " ".join(
        item.get("subjects", []) + item.get("bookshelves", [])
    )
    return classify(title, subjects)


def build_description(item):
    summary = clean_summary(
        (item.get("summaries") or [""])[0]
    )

    if len(summary) < 60:
        subjects = [
            clean_text(subject)
            for subject in item.get("subjects", [])[:5]
        ]
        summary = " ".join(subjects) if subjects else "A public-domain classic."

    summary = shorten(summary, 330)

    return (
        f"{summary} Read it free in the browser or download the original "
        "edition from Project Gutenberg."
    )


def eligible(item):
    formats = item.get("formats") or {}

    return (
        bool(clean_text(item.get("title")))
        and bool(item.get("id"))
        and item.get("copyright") is False
        and "en" in item.get("languages", [])
        and item.get("media_type") == "Text"
        and bool(item.get("summaries"))
        and bool(formats.get("text/html"))
        and bool(formats.get("image/jpeg"))
    )


def main():
    seen_titles = {
        normalize_title(book["title"]) for book in BOOKS
    }
    seen_gids = {
        book.get("gid") for book in BOOKS
        if book.get("source") == "gutenberg"
    }
    selected = []

    def add(item):
        if len(selected) >= TARGET or not eligible(item):
            return False

        gid = item["id"]
        title = clean_text(item["title"])
        key = normalize_title(title)

        if gid in seen_gids or key in seen_titles:
            return False

        seen_gids.add(gid)
        seen_titles.add(key)

        category = guess_category(item)

        selected.append({
            "slug": f"gutenberg-{gid}",
            "title": shorten(title, 195),
            "author": " & ".join(
                clean_author(author["name"])
                for author in item.get("authors", [])
            ) or "Unknown author",
            "publisher": "Project Gutenberg",
            "category": category,
            "description": build_description(item),
            "source": "remote",
            "gutenberg_id": gid,
            "external_url": item["formats"]["text/html"]
        })

        return True

    # Popular titles first: these are the ones readers are most likely to want.
    popular = []
    popular_first = 120

    for page in range(1, PAGES + 1):
        if len(popular) >= PAGES * PAGE_SIZE:
            break

        results = fetch_page(page)
        print(f"Popular p{page}: {len(results)} results")
        popular.extend(results)

        for item in results:
            if len(selected) < popular_first:
                add(item)

    # Add non-fiction candidates from targeted topic searches. Their category
    # is derived from the same rules as the rest of the catalogue, so a search
    # result that is really a novel still lands in Literature.
    for search in TOPIC_QUERIES:
        if len(selected) >= TARGET:
            break

        results = fetch_page(search=search)
        print(f"Topic '{search}': {len(results)} results")

        for item in results:
            if len(selected) >= TARGET:
                break
            add(item)

    # Complete the collection from the popularity list.
    if len(selected) < TARGET:
        for item in popular:
            if len(selected) >= TARGET:
                break
            add(item)

    selected.sort(
        key=lambda book: CATEGORY_ORDER.index(book["category"])
    )

    # Give every streamed book a small local cover so the shelves never
    # depend on Gutenberg's image CDN being available.
    write_covers(selected)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(
            {
                "source": "Gutendex / Project Gutenberg public-domain metadata",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "count": len(selected),
                "books": selected
            },
            indent=2,
            ensure_ascii=False
        ) + "\n",
        encoding="utf-8"
    )

    counts = {
        category: sum(
            1 for book in selected if book["category"] == category
        )
        for category in CATEGORY_ORDER
    }

    print(f"Wrote {len(selected)} books to {OUTPUT.relative_to(BASE_DIR)}")
    print("  " + ", ".join(f"{name}: {count}" for name, count in counts.items()))


if __name__ == "__main__":
    main()
