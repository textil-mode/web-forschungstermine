from pathlib import Path

from scraper.adapters.ditf import DitfAdapter

FIX = Path(__file__).parent / "fixtures" / "ditf.html"


def _events():
    return DitfAdapter().parse(FIX.read_text(encoding="utf-8"))


def test_finds_upcoming_event():
    assert len(_events()) >= 1


def test_title_has_no_date_prefix():
    evs = _events()
    ev = evs[0]
    assert not ev.title[:1].isdigit()       # Datum-Präfix entfernt
    assert ev.start.startswith("2026")
    assert "termindetails" in ev.url
    assert ev.institute_id == "ditf"
