from pathlib import Path

from scraper.adapters.hohenstein import HohensteinAdapter

FIX = Path(__file__).parent / "fixtures" / "hohenstein.html"


def _events():
    return HohensteinAdapter().parse(FIX.read_text(encoding="utf-8"))


def test_finds_multiple_events():
    assert len(_events()) >= 5


def test_events_are_valid():
    for ev in _events():
        assert ev.title and len(ev.title) > 3
        assert ev.start and ev.start[:2] == "20"        # ISO Jahr
        assert ev.url.startswith("https://www.hohenstein.de/de/termine/detail/")
        assert ev.institute_id == "hohenstein"


def test_soft_hyphens_removed():
    assert all("­" not in ev.title for ev in _events())


def test_detects_online():
    kinds = [ev for ev in _events() if ev.online]
    # Im Fixture gibt es mind. ein Online-Seminar/-Workshop
    assert any("online" in (ev.kind or "").lower() for ev in kinds)
