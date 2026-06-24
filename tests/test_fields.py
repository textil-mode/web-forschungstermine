from datetime import date

from scraper.build import build_events
from scraper.fields import classify, field_defs
from scraper.model import Event


def test_classify_kreislauf():
    assert "kreislauf" in classify("Webinar: Recycling von Textilabfällen")


def test_classify_multiple_fields():
    keys = classify("Smart Textiles für nachhaltige Medizinprodukte")
    assert "smart" in keys and "nachhaltigkeit" in keys and "medizin" in keys


def test_classify_none():
    assert classify("Allgemeine Mitgliederversammlung") == []


def test_field_defs_have_key_and_label():
    for f in field_defs():
        assert f["key"] and f["label"]


class _FakeAdapter:
    institute = "Fake"
    institute_id = "fake"

    def fetch(self):
        return [Event(title="Kolloquium Faserverbund & Recycling", institute="Fake",
                      institute_id="fake", start="2026-09-01", url="https://x/y")]


def test_build_attaches_fields():
    out = build_events([_FakeAdapter()], today=date(2026, 6, 24))
    assert "fields" in out[0]
    assert "kreislauf" in out[0]["fields"]
    assert "faser" in out[0]["fields"]
