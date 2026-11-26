# Check that every resource in the database has real, matching content.
#
# Run from the backend folder (needs `pip install pypdf`):
#   ../.venv/Scripts/python.exe tools/audit_library.py
#
# For each book it confirms the PDF exists, is complete, contains readable
# text throughout, and that its opening pages mention the catalogue title
# and author. Videos and covers are checked for their files or links.

import logging
import re
import sys
import unicodedata
from pathlib import Path

from pypdf import PdfReader

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import Config  # noqa: E402
from fetch_public_domain_covers import cover_state as cover_quality  # noqa: E402
from external_links import is_allowed_external_url  # noqa: E402
from models import Resource  # noqa: E402
from run import create_app  # noqa: E402

UPLOAD_DIR = Path(Config.UPLOAD_FOLDER)

logging.getLogger("pypdf").setLevel(logging.ERROR)

STOPWORDS = {
    "the", "and", "for", "with", "from", "into", "made", "its", "an",
    "of", "on", "in", "to", "a", "or", "full", "course", "edition"
}


def normalise(text):
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def title_words(title):
    words = normalise(title.split(":")[0]).split()
    return [word for word in words if word not in STOPWORDS and len(word) > 2]


def author_names(author):
    first_author = re.split(r",| and ", author or "")[0]
    words = normalise(first_author).split()
    return [words[-1]] if words else []


def page_text(reader, index):
    try:
        return reader.pages[index].extract_text() or ""
    except Exception:
        return ""


def audit_book(resource):
    issues = []

    if not resource.file_path:
        return ["no PDF attached"], None

    path = UPLOAD_DIR / resource.file_path

    if not path.is_file():
        return [f"file missing: {resource.file_path}"], None

    data = path.read_bytes()

    if not data.startswith(b"%PDF") or b"%%EOF" not in data[-2048:]:
        return ["file is not a complete PDF"], None

    try:
        reader = PdfReader(str(path))
        pages = len(reader.pages)
    except Exception as error:
        return [f"PDF cannot be opened ({error})"], None

    if pages < 5:
        issues.append(f"only {pages} pages")

    # Skip the title page and colophon written by build_library_assets.py,
    # so the match is made against the book's own text.
    first = 2 if "E-Library Classic Collection" in page_text(reader, 0) else 0
    opening = normalise(" ".join(
        page_text(reader, i) for i in range(first, min(pages, first + 10))
    ))
    samples = [page_text(reader, i) for i in {pages // 4, pages // 2, (3 * pages) // 4}]
    body_chars = sum(len(sample.strip()) for sample in samples)

    if not opening and body_chars == 0:
        issues.append("no extractable text (scanned images only)")
    else:
        words = title_words(resource.title)
        found = [word for word in words if word in opening]

        if words and len(found) / len(words) < 0.6:
            missing = sorted(set(words) - set(found))
            issues.append(f"title not found in opening pages (missing: {', '.join(missing)})")

        names = author_names(resource.author)

        if names and not all(name in opening for name in names):
            issues.append(f"author '{resource.author}' not found in opening pages")

        if body_chars < 300:
            issues.append("body pages look empty")

    return issues, pages


def audit_remote(resource):
    # Streamed books deliberately have no PDF. Their reading link must be an
    # approved HTTPS source and their generated cover must exist on disk.
    issues = []

    if not is_allowed_external_url(resource.external_url):
        issues.append(f"unrecognised reading link: {resource.external_url}")

    if resource.file_path:
        issues.append(f"streamed book should not have a PDF: {resource.file_path}")

    return issues


def audit_video(resource):
    url = resource.video_url or ""

    if not url:
        return ["no video attached"]

    if url.startswith("http"):
        if "youtube.com/watch?v=" not in url and "youtu.be/" not in url:
            return [f"unrecognised video link: {url}"]
        return []

    path = UPLOAD_DIR / url

    if not path.is_file():
        return [f"video file missing: {url}"]

    if b"ftyp" not in path.read_bytes()[:64]:
        return ["video file is not an MP4"]

    return []


def main():
    app = create_app()
    problems = 0

    with app.app_context():
        # Retired generated rows are kept for history but are not part of the
        # live catalogue, so only published resources are audited.
        resources = Resource.query.filter_by(
            is_published=True
        ).order_by(
            Resource.resource_type, Resource.title
        ).all()

        for resource in resources:
            if resource.resource_type == "book" and resource.external_url:
                issues, detail = audit_remote(resource), "streamed"
            elif resource.resource_type == "book":
                issues, pages = audit_book(resource)
                detail = f"{pages} pages" if pages else ""
            else:
                issues, detail = audit_video(resource), "video"

            if not resource.cover_image:
                issues.append("no cover image")
            else:
                quality = cover_quality({
                    "slug": resource.slug or "",
                    "cover_image": resource.cover_image
                })

                if quality in ("missing", "invalid", "placeholder"):
                    issues.append(
                        f"{quality} cover: {resource.cover_image}"
                    )
                elif not (UPLOAD_DIR / resource.cover_image).is_file():
                    issues.append(f"cover missing: {resource.cover_image}")

            status = "OK  " if not issues else "FAIL"
            problems += bool(issues)
            print(f"{status} [{resource.resource_type}] {resource.title} ({detail})")

            for issue in issues:
                print(f"       - {issue}")

        print()
        print(f"{len(resources)} resources checked, {problems} with problems.")

    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
