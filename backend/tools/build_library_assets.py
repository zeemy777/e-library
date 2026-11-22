# Build the real library assets used by seed_library.py.
#
# Run from the backend folder:
#   ../.venv/Scripts/python.exe tools/build_library_assets.py
#
# Books are downloaded from Project Gutenberg or other openly licensed
# sources. Gutenberg texts are typeset into PDF with headless Chrome so
# every book can be read online and downloaded.

import html
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from library_catalogue import BOOKS, VIDEOS  # noqa: E402

UPLOAD_DIR = BASE_DIR / "uploads"
BOOK_DIR = UPLOAD_DIR / "books"
COVER_DIR = UPLOAD_DIR / "covers"
VIDEO_DIR = UPLOAD_DIR / "videos"

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) E-Library-Demo/1.0"

CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
]


def ensure_folders():
    for folder in (BOOK_DIR, COVER_DIR, VIDEO_DIR):
        folder.mkdir(parents=True, exist_ok=True)


def fetch(url, destination, minimum_size=1024):
    """Download a URL, keeping a valid existing file untouched."""

    if destination.exists() and destination.stat().st_size >= minimum_size:
        return True

    destination.parent.mkdir(parents=True, exist_ok=True)

    try:
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(request, timeout=120) as response:
            with open(destination, "wb") as handle:
                shutil.copyfileobj(response, handle)
    except Exception:
        # Some hosts block urllib but accept curl.
        result = subprocess.run(
            [
                "curl", "-sL", "--fail", "--max-time", "180",
                "-A", USER_AGENT, "-o", str(destination), url
            ],
            capture_output=True
        )
        if result.returncode != 0:
            destination.unlink(missing_ok=True)
            return False

    if not destination.exists() or destination.stat().st_size < minimum_size:
        destination.unlink(missing_ok=True)
        return False

    return True


def is_pdf(path):
    try:
        with open(path, "rb") as handle:
            if handle.read(4) != b"%PDF":
                return False

            handle.seek(0, 2)
            handle.seek(max(0, handle.tell() - 2048))
            return b"%%EOF" in handle.read()
    except OSError:
        return False


def is_jpeg(path):
    try:
        return path.read_bytes()[:2] == b"\xff\xd8"
    except OSError:
        return False


def is_video(path):
    try:
        head = path.read_bytes()[:64]
    except OSError:
        return False

    return b"ftyp" in head


def find_chrome():
    for candidate in CHROME_CANDIDATES:
        if Path(candidate).is_file():
            return candidate

    raise RuntimeError(
        "Chrome or Edge is required to build the book PDFs."
    )


def gutenberg_text(book_id):
    url = f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt"
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    with urllib.request.urlopen(request, timeout=120) as response:
        text = response.read().decode("utf-8", "replace")

    text = text.replace("\r\n", "\n").replace("\r", "\n")

    start = text.find("*** START OF THE PROJECT GUTENBERG EBOOK")
    if start != -1:
        line_end = text.find("\n", start)
        if line_end != -1:
            text = text[line_end + 1:]

    end = text.find("*** END OF THE PROJECT GUTENBERG EBOOK")
    if end != -1:
        text = text[:end]

    return text.strip()


def text_to_html(book, text):
    blocks = [block.strip() for block in re.split(r"\n\s*\n", text) if block.strip()]
    parts = []

    for block in blocks:
        first_line = block.split("\n", 1)[0].strip()
        is_heading = (
            len(first_line) <= 70
            and "\n" not in block
            and (
                re.fullmatch(r"[A-Z0-9 ,.:;'!?()\-]+", first_line)
                or re.match(r"^(Chapter|CHAPTER|Book|BOOK|Part|PART)\b", first_line)
            )
        )

        if is_heading and not re.fullmatch(r"[0-9IVXLCDM]+", first_line):
            parts.append(f"<h2>{html.escape(first_line)}</h2>")
        else:
            clean = html.escape(" ".join(block.split()))
            parts.append(f"<p>{clean}</p>")

    title = html.escape(book["title"])
    author = html.escape(book["author"])

    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
@page {{ size: A5; margin: 17mm 16mm 18mm; }}
html {{ -webkit-print-color-adjust: exact; }}
body {{
  margin: 0;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 10.5pt;
  line-height: 1.62;
  color: #1d2433;
}}
.title-page {{
  height: 160mm;
  display: flex;
  flex-direction: column;
  justify-content: center;
  text-align: center;
  break-after: page;
}}
.brand {{
  letter-spacing: 3px;
  font-size: 8pt;
  text-transform: uppercase;
  color: #5a6b8c;
}}
h1 {{
  font-size: 25pt;
  line-height: 1.18;
  margin: 16px 0 10px;
  font-weight: 600;
}}
.author {{
  font-size: 12pt;
  font-style: italic;
  color: #44526e;
}}
.source {{
  margin-top: 42px;
  font-size: 8pt;
  color: #7a8599;
}}
.colophon {{
  break-after: page;
  padding-top: 40mm;
  font-size: 9pt;
  line-height: 1.7;
  color: #44526e;
}}
.colophon h2 {{
  font-size: 13pt;
  letter-spacing: 1px;
  margin-bottom: 14px;
  color: #1d2433;
}}
.colophon p {{
  text-align: left;
  text-indent: 0;
}}
h2 {{
  font-size: 13pt;
  margin: 26px 0 12px;
  text-align: center;
  letter-spacing: 1px;
  break-after: avoid;
}}
p {{
  margin: 0 0 7px;
  text-align: justify;
  text-indent: 18px;
}}
</style>
</head>
<body>
<section class="title-page">
  <p class="brand">E-Library Classic Collection</p>
  <h1>{title}</h1>
  <p class="author">{author}</p>
  <p class="source">{html.escape(book["publisher"])} · Project Gutenberg eBook #{book["gid"]}</p>
</section>
<section class="colophon">
  <h2>About this edition</h2>
  <p>
    This reading edition was prepared for the E-Library demo from the
    public-domain text of <em>{title}</em> by {author}.
  </p>
  <p>
    Source: Project Gutenberg eBook #{book["gid"]},
    https://www.gutenberg.org/ebooks/{book["gid"]}. The text is made
    available under the Project Gutenberg License.
  </p>
  <p>
    The cover artwork shown in the catalogue is the Project Gutenberg
    cover for the same eBook.
  </p>
</section>
{chr(10).join(parts)}
</body>
</html>
"""


def build_pdf(book, chrome, workdir):
    slug = book["slug"]
    destination = BOOK_DIR / f"{slug}.pdf"

    if destination.exists() and is_pdf(destination) and destination.stat().st_size > 5000:
        print(f"  pdf      {slug} (exists)")
        return

    try:
        text = gutenberg_text(book["gid"])
    except Exception as error:
        print(f"  pdf      {slug} FAILED {error}")
        return

    page = workdir / f"{slug}.html"
    page.write_text(text_to_html(book, text), encoding="utf-8")

    try:
        result = subprocess.run(
            [
                chrome,
                "--headless=new",
                "--disable-gpu",
                "--no-pdf-header-footer",
                "--run-all-compositor-stages-before-draw",
                f"--user-data-dir={workdir / ('chrome-profile-' + slug)}",
                f"--print-to-pdf={destination}",
                page.as_uri()
            ],
            capture_output=True,
            timeout=300
        )
    except Exception as error:
        destination.unlink(missing_ok=True)
        print(f"  pdf      {slug} FAILED {error}")
        return

    if result.returncode != 0 or not is_pdf(destination):
        destination.unlink(missing_ok=True)
        error = result.stderr.decode("utf-8", "replace")[-300:]
        print(f"  pdf      {slug} FAILED {error}")
        return

    size = destination.stat().st_size / 1024
    print(f"  pdf      {slug} ({size:.0f} KB)")


def download_cover(book):
    cover_url = book.get("cover_url")

    if not cover_url and book.get("source") == "gutenberg":
        gid = book["gid"]
        cover_url = (
            f"https://www.gutenberg.org/cache/epub/{gid}/"
            f"pg{gid}.cover.medium.jpg"
        )

    if not cover_url:
        return

    destination = COVER_DIR / f"{book['slug']}.jpg"

    if destination.exists() and is_jpeg(destination):
        return

    destination.unlink(missing_ok=True)

    if fetch(cover_url, destination, minimum_size=3000) and is_jpeg(destination):
        print(f"  cover    {book['slug']}")
    else:
        destination.unlink(missing_ok=True)
        print(f"  cover    {book['slug']} (not available)")


def main():
    ensure_folders()
    chrome = find_chrome()

    with tempfile.TemporaryDirectory() as build_dir:
        workdir = Path(build_dir)

        print("Downloading openly licensed books")
        for book in BOOKS:
            if book["source"] == "url":
                destination = BOOK_DIR / f"{book['slug']}.pdf"

                if destination.exists() and is_pdf(destination):
                    print(f"  pdf      {book['slug']} (exists)")
                else:
                    destination.unlink(missing_ok=True)

                    if fetch(book["url"], destination, minimum_size=10000) and is_pdf(destination):
                        size = destination.stat().st_size / (1024 * 1024)
                        print(f"  pdf      {book['slug']} ({size:.1f} MB)")
                    else:
                        destination.unlink(missing_ok=True)
                        print(f"  pdf      {book['slug']} FAILED")
            else:
                build_pdf(book, chrome, workdir)

            download_cover(book)

    print("Downloading video assets")
    for video in VIDEOS:
        cover_url = video.get("cover_url")

        if cover_url:
            destination = COVER_DIR / f"{video['slug']}.jpg"

            if destination.exists() and not is_jpeg(destination):
                destination.unlink()

            if fetch(cover_url, destination, minimum_size=3000) and is_jpeg(destination):
                print(f"  cover    {video['slug']}")
            else:
                destination.unlink(missing_ok=True)

        download_url = video.get("download_url")

        if not download_url:
            continue

        destination = VIDEO_DIR / f"{video['slug']}.mp4"

        if destination.exists() and is_video(destination):
            print(f"  video    {video['slug']} (exists)")
        else:
            destination.unlink(missing_ok=True)

            if fetch(download_url, destination, minimum_size=100000) and is_video(destination):
                size = destination.stat().st_size / (1024 * 1024)
                print(f"  video    {video['slug']} ({size:.1f} MB)")
            else:
                destination.unlink(missing_ok=True)
                print(f"  video    {video['slug']} FAILED")

    print("Asset build complete.")


if __name__ == "__main__":
    main()
