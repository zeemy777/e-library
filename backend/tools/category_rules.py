# Shared category rules for the remote Gutenberg catalogue.
#
# Titles are a much stronger signal than descriptions, so they are weighted
# more heavily. Phrases such as "science fiction" and "natural history" are
# removed before matching: they used to file horror stories under Science and
# Pliny under History.

import re

CATEGORY_ORDER = [
    "Technology",
    "Science",
    "Business",
    "Fantasy",
    "Literature",
    "Mathematics",
    "History"
]

PATTERNS = {
    "Technology": [
        r"\bcomputer", r"\bcomputing", r"\bprogramming", r"\bsoftware",
        r"\binternet", r"\bengineering", r"\belectric", r"\btelegraph",
        r"\btelephone", r"\bmachinery", r"\bwireless", r"\bradio\b",
        r"\bautomobile", r"\bmanufactur", r"\btechnology", r"\btechnical",
        r"\bsteam engine"
    ],
    "Science": [
        r"\bastronom", r"\bbiolog", r"\bchemistr", r"\bphysic",
        r"\bbotan", r"\bzoolog", r"\bgeolog", r"\bevolution",
        r"\banatom", r"\bmicroscop", r"\bscientific", r"\bpopular science",
        r"\bmedicine", r"\bmedical", r"\bheredity", r"\bgenetic",
        r"\bnatural philosophy", r"\bnatural history"
    ],
    "Business": [
        r"\beconomic", r"\bcommerce", r"\bcommercial", r"\bfinanc",
        r"\bbanking", r"\binvestment", r"\baccounting", r"\bmanagement",
        r"\bmarketing", r"\bbusiness", r"\bprice list", r"\bwall street",
        r"\bstock market", r"\btrade union", r"\blabour", r"\blabor\b",
        r"\bcatalog\b"
    ],
    "Mathematics": [
        r"\bmathematic", r"\bcalculus", r"\balgebra", r"\bgeometry",
        r"\barithmetic", r"\btrigonometr", r"\bstatistic", r"\bprobabilit",
        r"\bnumber theory"
    ],
    "History": [
        r"\bhistory\b", r"\bhistoric", r"\bancient", r"\bcivilisation",
        r"\bcivilization", r"\brevolution", r"\bempire", r"\bbiograph",
        r"\bexploration", r"\bconstitution", r"\bmedieval",
        r"\bmiddle ages", r"\barchaeolog", r"\bchronicle", r"\bpolitical",
        r"\bdemocracy", r"\bgovernment"
    ]
}

FICTION_PATTERNS = [
    r"\bshort stor", r"\bnovel\b", r"\bnovella", r"\bfiction\b",
    r"\bgothic", r"\bhorror", r"\bpoetry\b", r"\bpoems?\b",
    r"\btales?\b", r"\bromance\b", r"\bfantasy\b", r"\bdrama\b"
]

# Strong title words move a book to Fantasy; weaker words in a summary need
# several hits. Science fiction stays in Literature unless it is also a
# fairy tale, myth or magical romance.
FANTASY_PATTERNS = [
    r"\bfantas", r"\bfairy", r"\bfaer", r"\bmagic", r"\benchant",
    r"\bdragon", r"\bwizard", r"\bsorcer", r"\bwitch", r"\bgoblin",
    r"\bgnome", r"\bgiant", r"\belves\b", r"\belf\b", r"\bmermaid",
    r"\bogre", r"\btroll", r"\bmyth", r"\blegend", r"\bmarvel",
    r"\bother ?world", r"\boccult", r"\bphantom", r"\bgenie",
    r"\balchem"
]

# "Fantasy" also names a musical form and appears as a subject tag on some
# memoirs and psychology texts. Those should not land on the fantasy shelf.
FANTASY_EXCLUDED_TITLE = [
    r"\bpsycholog", r"\bfantasia\b", r"\bfantasie\b", r"\bfugues?",
    r"\bmusical fantas"
]
FANTASY_EXCLUDED_DESCRIPTION = [
    r"\bpsychoanalys", r"\bautobiograph", r"\bmemoir", r"\bpiano music",
    r"\bcanons and fugues", r"\borchestra", r"\bmusical fantas"
]

COMPILED = {
    category: [re.compile(pattern) for pattern in patterns]
    for category, patterns in PATTERNS.items()
}
FICTION = [re.compile(pattern) for pattern in FICTION_PATTERNS]
FANTASY = [re.compile(pattern) for pattern in FANTASY_PATTERNS]
FANTASY_TITLE_EXCLUDED = [
    re.compile(pattern) for pattern in FANTASY_EXCLUDED_TITLE
]
FANTASY_DESCRIPTION_EXCLUDED = [
    re.compile(pattern) for pattern in FANTASY_EXCLUDED_DESCRIPTION
]
GENRE_CATEGORIES = {"Fantasy", "Literature"}


def normalize(text):
    text = (text or "").lower()
    # These phrases contain generic keywords that would skew the scores.
    text = re.sub(r"science[-\s]*fiction", " ", text)
    text = re.sub(r"natural history", " natural science ", text)
    return text


def classify(title, description=""):
    """Pick a category for one book. Unknown or fictional books go to Literature."""

    title_text = normalize(title)
    description_text = normalize(description)

    scores = {}
    title_hits = {}

    for category, patterns in COMPILED.items():
        title_hits[category] = sum(
            1 for pattern in patterns if pattern.search(title_text)
        )
        description_hits = sum(
            1 for pattern in patterns if pattern.search(description_text)
        )
        scores[category] = title_hits[category] * 3 + description_hits

    fiction = (
        any(pattern.search(description_text) for pattern in FICTION)
        or any(pattern.search(title_text) for pattern in FANTASY)
    )

    # A single vague word in a summary is not enough to move a book out of
    # the fiction shelves. Fictional works need a clearer non-fiction signal.
    threshold = 4 if fiction else 2

    if fiction and max(title_hits.values()) == 0:
        threshold = 5

    non_fiction = [
        category for category in CATEGORY_ORDER
        if category not in GENRE_CATEGORIES
    ]
    best = max(non_fiction, key=lambda category: scores[category])

    fantasy_title_hits = sum(
        1 for pattern in FANTASY if pattern.search(title_text)
    )
    fantasy_description_hits = sum(
        1 for pattern in FANTASY if pattern.search(description_text)
    )
    excluded_from_fantasy = (
        any(pattern.search(title_text) for pattern in FANTASY_TITLE_EXCLUDED)
        or any(
            pattern.search(description_text)
            for pattern in FANTASY_DESCRIPTION_EXCLUDED
        )
    )
    fantasy_score = 0 if excluded_from_fantasy else (
        fantasy_title_hits * 3 + fantasy_description_hits
    )

    if fantasy_title_hits and fantasy_score >= 3:
        return "Fantasy"

    if fantasy_score >= 6 and fantasy_score >= scores[best]:
        return "Fantasy"

    return best if scores[best] >= threshold else "Literature"
