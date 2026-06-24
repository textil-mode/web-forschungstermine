from datetime import date

import pytest

from app import db
from scraper.model import Event


@pytest.fixture()
def tmpdb(tmp_path):
    db.DB_PATH = tmp_path / "t.db"
    db.init_db()
    return db.DB_PATH


def _ev(title="Kolloquium Faserverbund", start="2026-09-01", iid="ditf"):
    return Event(title=title, institute="DITF", institute_id=iid,
                 start=start, url="https://x/y").to_dict()


def test_upsert_and_future_filter(tmpdb):
    db.upsert_event(_ev(start="2026-01-01"))   # vergangen
    db.upsert_event(_ev(title="Zukunft", start="2026-12-01"))
    out = db.get_events(today=date(2026, 6, 24))
    assert [e["title"] for e in out] == ["Zukunft"]


def test_pending_dedup_against_events(tmpdb):
    ev = _ev()
    db.upsert_event(ev)
    assert db.add_pending(ev, 0.9) is False    # schon live -> kein Vorschlag


def test_approve_moves_to_events(tmpdb):
    ev = _ev(title="KI-Termin", start="2026-10-01")
    assert db.add_pending(ev, 0.8) is True
    assert db.get_pending()[0]["title"] == "KI-Termin"
    assert db.approve(ev["id"]) is True
    assert any(e["id"] == ev["id"] for e in db.get_events(today=date(2026, 6, 24)))
    assert db.get_pending() == []


def test_reject_is_permanent(tmpdb):
    ev = _ev(title="Spam", start="2026-10-01")
    db.add_pending(ev, 0.3)
    assert db.reject(ev["id"]) is True
    assert db.get_pending() == []
    assert db.add_pending(ev, 0.3) is False    # verworfen -> kommt nicht wieder
