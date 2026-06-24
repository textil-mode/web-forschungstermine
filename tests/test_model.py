import pytest

from scraper.model import Event, slugify


def test_event_id_is_stable_slug():
    e = Event(title="Kolloquium: Faserverbund", institute="DITF Denkendorf",
              institute_id="ditf", start="2026-09-12", url="https://x/y")
    assert e.id == "ditf-2026-09-12-kolloquium-faserverbund"


def test_event_requires_title():
    with pytest.raises(ValueError):
        Event(title="", institute="DITF", institute_id="ditf",
              start="2026-09-12", url="https://x/y")


def test_event_requires_iso_start():
    with pytest.raises(ValueError):
        Event(title="X", institute="DITF", institute_id="ditf",
              start="12.09.2026", url="https://x/y")


def test_event_requires_valid_url():
    with pytest.raises(ValueError):
        Event(title="X", institute="DITF", institute_id="ditf",
              start="2026-09-12", url="")


def test_slugify_handles_umlauts():
    assert slugify("Textilveredlung & Färben") == "textilveredlung-faerben"


def test_to_dict_roundtrip_fields():
    e = Event(title="Webinar", institute="STFI", institute_id="stfi",
              start="2026-10-01", url="https://stfi.de/x", online=True, kind="Webinar")
    d = e.to_dict()
    assert d["online"] is True
    assert d["kind"] == "Webinar"
    assert d["id"] == "stfi-2026-10-01-webinar"
