from tools.category_rules import classify


def test_fantasy_titles_get_their_own_shelf():
    assert classify(
        "The Enchanted Castle",
        "A children's fantasy novel about a magical house."
    ) == "Fantasy"
    assert classify(
        "The Princess and the Goblin",
        "A fairy tale for children."
    ) == "Fantasy"


def test_fiction_is_not_swept_into_non_fiction():
    assert classify(
        "The Last of the Mohicans",
        "A historical romance novel set during the French and Indian War."
    ) == "Literature"


def test_non_fiction_still_wins():
    assert classify(
        "Calculus Made Easy",
        "An introduction to the differential calculus."
    ) == "Mathematics"


def test_fantasy_word_does_not_capture_psychology_or_music():
    assert classify(
        "The psychology of day-dreams",
        "Dreams; Psychoanalysis; Psychology; Fantasy"
    ) == "Literature"
    assert classify(
        "Fantasia and fugue in A minor",
        "Canons and fugues; Piano music"
    ) == "Literature"
