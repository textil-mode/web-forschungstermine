from pathlib import Path

from scraper.adapters.wfk import WfkAdapter, _parse_range

FIX = Path(__file__).parent / "fixtures" / "wfk.html"


def _events():
    return WfkAdapter().parse(FIX.read_text(encoding="utf-8"))


def test_parse_range_within_month():
    assert _parse_range("09. – 11.09.2026") == ("2026-09-09", "2026-09-11")


def test_parse_range_single():
    assert _parse_range("11.09.2026") == ("2026-09-11", None)


def test_finds_events():
    assert len(_events()) >= 2


def test_events_valid():
    for e in _events():
        assert e.start[:4] == "2026"
        assert e.url.startswith("http")
        assert e.institute_id == "wfk"
