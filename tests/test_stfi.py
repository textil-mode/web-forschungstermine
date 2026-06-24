from pathlib import Path

from scraper.adapters.stfi import StfiAdapter, _parse_date

FIX = Path(__file__).parent / "fixtures" / "stfi.html"


def _events():
    return StfiAdapter().parse(FIX.read_text(encoding="utf-8"))


def test_parse_simple_date():
    assert _parse_date("17.6.2026") == "2026-06-17"


def test_parse_messy_range():
    assert _parse_date("22.-23.-10.2026") == "2026-10-22"


def test_matches_own_events_only():
    evs = _events()
    # Dresdner Kolloquium ist STFI-eigen (Card) und in der Tabelle datiert
    assert any("Dresdner Kolloquium" in e.title for e in evs)
    # Fremdtermine (z. B. Innovationstag des BMWE) dürfen NICHT auftauchen
    assert not any("BMWE" in e.title for e in evs)


def test_events_valid():
    for e in _events():
        assert e.url.startswith("https://www.stfi.de/")
        assert e.institute_id == "stfi"
        assert e.start[:4] == "2026"
