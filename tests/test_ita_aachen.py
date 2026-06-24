from pathlib import Path

from scraper.adapters.ita_aachen import ItaAachenAdapter

FIX = Path(__file__).parent / "fixtures" / "ita_aachen.html"


def _events():
    return ItaAachenAdapter().parse(FIX.read_text(encoding="utf-8"))


def test_finds_events():
    assert len(_events()) >= 1


def test_events_valid():
    evs = _events()
    assert any("WIRKsam" in e.title for e in evs)
    for e in evs:
        assert e.start[:4] == "2026"
        assert e.url.startswith("https://www.ita.rwth-aachen.de/")
        assert e.institute_id == "ita-aachen"
