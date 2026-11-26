# Reclassify the committed remote catalogue using shared category rules.
#
#   ../.venv/Scripts/python.exe tools/reclassify_remote_catalogue.py
#
# No network access is needed: titles and descriptions in the JSON are enough.
# Safe to re-run. It also groups the entries by category for a tidy catalogue.

import json
from collections import Counter
from pathlib import Path

from category_rules import CATEGORY_ORDER, classify

BASE_DIR = Path(__file__).resolve().parents[1]
CATALOGUE = BASE_DIR / "catalogue" / "remote_books.json"


def main():
    data = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    books = data.get("books", [])

    before = Counter(book["category"] for book in books)

    for book in books:
        book.pop("cover_url", None)
        book["category"] = classify(
            book["title"], book.get("description", "")
        )

    books.sort(key=lambda book: CATEGORY_ORDER.index(book["category"]))

    CATALOGUE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8"
    )

    after = Counter(book["category"] for book in books)

    print(f"Reclassified {len(books)} books in {CATALOGUE.name}.")
    for category in CATEGORY_ORDER:
        print(f"  {category}: {before[category]} -> {after[category]}")


if __name__ == "__main__":
    main()
