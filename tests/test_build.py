from datetime import date

from scraper.build import build_events
from scraper.model import Event


class _FakeAdapter:
    institute = "Fake"
    institute_id = "fake"

    def __init__(self, events):
        self._events = events

    def fetch(self):
        return self._events


class _BrokenAdapter:
    institute = "Broken"
    institute_id = "broken"

    def fetch(self):
        raise RuntimeError("Seite kaputt")


def _ev(title, start, iid="fake"):
    return Event(title=title, institute="Fake", institute_id=iid,
                 start=start, url="https://x/y")


def test_filters_past_events():
    a = _FakeAdapter([_ev("Vergangen", "2026-01-01"), _ev("Zukunft", "2026-12-01")])
    out = build_events([a], today=date(2026, 6, 24))
    titles = [e["title"] for e in out]
    assert titles == ["Zukunft"]


def test_sorts_by_start():
    a = _FakeAdapter([_ev("Spaeter", "2026-12-01"), _ev("Frueher", "2026-07-01")])
    out = build_events([a], today=date(2026, 6, 24))
    assert [e["title"] for e in out] == ["Frueher", "Spaeter"]


def test_broken_adapter_is_skipped():
    good = _FakeAdapter([_ev("Gut", "2026-09-01")])
    out = build_events([_BrokenAdapter(), good], today=date(2026, 6, 24))
    assert [e["title"] for e in out] == ["Gut"]


def test_dedup_by_id():
    a = _FakeAdapter([_ev("Doppelt", "2026-09-01"), _ev("Doppelt", "2026-09-01")])
    out = build_events([a], today=date(2026, 6, 24))
    assert len(out) == 1
