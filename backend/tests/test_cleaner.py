from app.processing.cleaner import clean_text


def test_joins_hyphenated_words_and_collapses_whitespace():
    assert clean_text("pres-\nsure   valve\n\n\n\nOK") == "pressure valve\n\nOK"


def test_strips_null_bytes():
    assert clean_text("a\x00b") == "ab"
