# Typographic SVG covers for streamed books.
#
# Gutenberg's cover CDN is not always reachable, so remote catalogue rows get
# a small locally generated cover instead. Every cover is a few hundred bytes,
# loads offline and keeps the warm library palette consistent.

import textwrap
from pathlib import Path
from xml.sax.saxutils import escape

BASE_DIR = Path(__file__).resolve().parents[1]
COVER_DIR = BASE_DIR / "uploads" / "covers"

PALETTES = [
    ("#2e1b0f", "#9a5420", "#f0b56a"),
    ("#17332c", "#3f7a5f", "#a7d9bf"),
    ("#322344", "#73518f", "#d9b9ef"),
    ("#3d2514", "#b26f2e", "#f2c489"),
    ("#152c3c", "#3c718c", "#a9d2e5"),
    ("#3b1d22", "#96494b", "#f0b0a6"),
]


def cover_relative_path(slug):
    return f"covers/{slug}.svg"


def wrapped_lines(value, width, maximum):
    lines = textwrap.wrap(
        " ".join(str(value or "").split()),
        width=width,
        break_long_words=True,
        break_on_hyphens=False
    ) or ["Untitled"]

    if len(lines) > maximum:
        lines = lines[:maximum]
        lines[-1] = lines[-1][:width - 1].rstrip() + "…"

    return lines


def make_svg(book):
    gid = book.get("gutenberg_id") or 0
    dark, light, highlight = PALETTES[gid % len(PALETTES)]
    tilt = (gid % 7) - 3

    title_lines = wrapped_lines(book["title"], 21, 5)
    author_lines = wrapped_lines(book.get("author"), 27, 2)

    title_size = 32 if max(len(line) for line in title_lines) > 17 else 37
    title_y = 190 - (len(title_lines) - 1) * 21

    title_markup = "\n".join(
        f'      <tspan x="56" y="{title_y + index * 42}">'
        f'{escape(line)}</tspan>'
        for index, line in enumerate(title_lines)
    )
    author_y = 430 - (len(author_lines) - 1) * 24
    author_markup = "\n".join(
        f'      <tspan x="56" y="{author_y + index * 24}">'
        f'{escape(line)}</tspan>'
        for index, line in enumerate(author_lines)
    )

    safe_label = escape(book["title"], {'"': "&quot;"})
    source_label = book.get("source_label", "PROJECT GUTENBERG")

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 600" role="img" aria-label="{safe_label}">
  <defs>
    <linearGradient id="cover" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{dark}"/>
      <stop offset="1" stop-color="{light}"/>
    </linearGradient>
  </defs>
  <rect width="400" height="600" fill="url(#cover)"/>
  <g transform="rotate({tilt} 200 300)" opacity="0.16" fill="none" stroke="{highlight}" stroke-width="2">
    <circle cx="312" cy="128" r="66"/>
    <circle cx="312" cy="128" r="42"/>
    <path d="M246 128h132M312 62v132"/>
  </g>
  <rect x="18" y="18" width="364" height="564" rx="6" fill="none" stroke="{highlight}" stroke-opacity="0.45"/>
  <rect x="34" y="70" width="6" height="80" fill="{highlight}" opacity="0.85"/>
  <g font-family="Georgia, 'Times New Roman', serif" fill="#fff8ee">
    <text font-size="30" font-weight="700" letter-spacing="1">{title_markup}
    </text>
    <text x="56" y="112" font-size="12" letter-spacing="4" fill="{highlight}">{escape(source_label)}</text>
    <text font-size="17" opacity="0.9">{author_markup}
    </text>
  </g>
  <line x1="56" y1="500" x2="344" y2="500" stroke="{highlight}" stroke-opacity="0.55"/>
  <text x="56" y="534" font-family="Arial, sans-serif" font-size="11" letter-spacing="3" fill="{highlight}" opacity="0.85">PUBLIC DOMAIN · FREE TO READ</text>
</svg>
'''


def write_covers(books):
    COVER_DIR.mkdir(parents=True, exist_ok=True)

    for book in books:
        path = COVER_DIR / f"{book['slug']}.svg"
        path.write_text(make_svg(book), encoding="utf-8")
        book["cover_image"] = cover_relative_path(book["slug"])

    return len(books)
