from datetime import date

import pytest

import scraper.registry as registry
from app import db
from app.refresh import run_refresh
from scraper.model import Event


class _FakeAdapter:
    institute = "Fake"
    institute_id = "fake"

    def fetch(self):
        return [
            Event(title="Kolloquium Recycling", institute="Fake", institute_id="fake",
                  start="2026-09-01", url="https://x/y"),
            Event(title="Vergangen", institute="Fake", institute_id="fake",
                  start="2026-01-01", url="https://x/z"),
        ]


@pytest.fixture()
def tmpdb(tmp_path, monkeypatch):
    db.DB_PATH = tmp_path / "t.db"
    db.init_db()
    monkeypatch.setattr(registry, "ACTIVE_ADAPTERS", [_FakeAdapter()])
    return db.DB_PATH


def test_refresh_fills_events_without_ki(tmpdb):
    summary = run_refresh(today=date(2026, 6, 24), with_ki=False)
    assert summary["structured"] == 1          # nur der künftige Termin
    events = db.get_events(today=date(2026, 6, 24))
    assert len(events) == 1
    assert events[0]["title"] == "Kolloquium Recycling"
    assert "kreislauf" in events[0]["fields"]   # Klassifizierung greift
