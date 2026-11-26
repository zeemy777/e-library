# Add locally generated covers to the committed remote catalogue.
#
#   ../.venv/Scripts/python.exe tools/build_remote_covers.py
#
# Safe to re-run: existing SVG files are replaced and the JSON is updated in
# place. No network access is needed.

import json
from pathlib import Path

from remote_covers import write_covers

BASE_DIR = Path(__file__).resolve().parents[1]
CATALOGUE = BASE_DIR / "catalogue" / "remote_books.json"


def main():
    data = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    books = data.get("books", [])

    for book in books:
        book.pop("cover_url", None)

    count = write_covers(books)

    CATALOGUE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8"
    )

    print(f"Generated {count} covers in uploads/covers and updated {CATALOGUE.name}.")


if __name__ == "__main__":
    main()
