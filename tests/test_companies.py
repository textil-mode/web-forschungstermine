import pytest
from fastapi.testclient import TestClient

from app import db, mail


@pytest.fixture()
def tmpdb(tmp_path):
    db.DB_PATH = tmp_path / "t.db"
    db.init_db()
    return db.DB_PATH


@pytest.fixture()
def client(tmpdb, monkeypatch):
    # Mailversand im Test neutralisieren.
    monkeypatch.setattr(mail, "send_company_notification", lambda c: False)
    from app.api import app
    return TestClient(app)


def test_add_and_get_company(tmpdb):
    rid = db.add_company({"company": "Muster GmbH", "email": "a@b.de", "interest": "Recycling"})
    assert isinstance(rid, int)
    rows = db.get_companies()
    assert len(rows) == 1
    assert rows[0]["company"] == "Muster GmbH"
    assert rows[0]["email"] == "a@b.de"
    assert rows[0]["phone"] is None          # leere Felder werden None


def test_post_company_ok(client):
    res = client.post("/api/companies", data={"company": "Acme AG", "email": "x@acme.de"})
    assert res.status_code == 200
    assert res.json()["ok"] is True
    assert db.get_companies()[0]["company"] == "Acme AG"


def test_post_company_requires_email(client):
    res = client.post("/api/companies", data={"company": "Ohne Mail"})
    assert res.status_code == 422
    assert res.json()["ok"] is False
    assert db.get_companies() == []          # nichts gespeichert


def test_honeypot_is_dropped(client):
    res = client.post("/api/companies",
                      data={"company": "Bot", "email": "b@b.de", "hp": "ich-bin-bot"})
    assert res.status_code == 200
    assert res.json()["ok"] is True
    assert db.get_companies() == []          # Bot-Eintrag nicht gespeichert


def test_mail_noop_without_config(monkeypatch):
    for var in ("SMTP_HOST", "SMTP_USER", "SMTP_PASS", "MAIL_TO"):
        monkeypatch.delenv(var, raising=False)
    assert mail.send_company_notification({"company": "X"}) is False
