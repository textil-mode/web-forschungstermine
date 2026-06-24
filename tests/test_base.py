from scraper.adapters.base import parse_german_date


def test_parse_long_german_date():
    assert parse_german_date("12. September 2026") == "2026-09-12"


def test_parse_numeric_german_date():
    assert parse_german_date("am 05.03.2026 findet statt") == "2026-03-05"


def test_parse_iso_date():
    assert parse_german_date("2026-10-08") == "2026-10-08"


def test_parse_abbrev_month():
    assert parse_german_date("24. Sep 2026") == "2026-09-24"


def test_parse_unknown_returns_none():
    assert parse_german_date("nächsten Frühling") is None
