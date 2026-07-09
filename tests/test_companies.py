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
    rid = db.add_company({
        "company": "Muster GmbH", "first_name": "Erika", "last_name": "Muster",
        "email": "a@b.de", "website": "https://muster.de", "request_type": "A | ...",
        "company_desc": "Wir weben.", "anonymous": "Nein", "challenge_desc": "Recycling.",
        "innovation": ["Recycling-Technologien: ...", "Upcycling & Design for Circularity: ..."],
        "newsletter": "Ja", "association": "Südwesttextil e. V.",
    })
    assert isinstance(rid, int)
    rows = db.get_companies()
    assert len(rows) == 1
    r = rows[0]
    assert r["company"] == "Muster GmbH"
    assert r["first_name"] == "Erika"
    assert r["innovation"] == ["Recycling-Technologien: ...", "Upcycling & Design for Circularity: ..."]
    assert r["newsletter"] == "Ja"


def test_post_company_ok(client):
    res = client.post("/api/companies", data={
        "company": "Acme AG", "email": "x@acme.de", "first_name": "Max",
        "innovation": ["A", "B"], "anonymous": "Ja",
    })
    assert res.status_code == 200
    assert res.json()["ok"] is True
    row = db.get_companies()[0]
    assert row["company"] == "Acme AG"
    assert row["innovation"] == ["A", "B"]        # Mehrfachauswahl gespeichert


def test_post_company_requires_email(client):
    res = client.post("/api/companies", data={"company": "Ohne Mail"})
    assert res.status_code == 422
    assert res.json()["ok"] is False
    assert db.get_companies() == []                # nichts gespeichert


def test_honeypot_is_dropped(client):
    res = client.post("/api/companies",
                      data={"company": "Bot", "email": "b@b.de", "hp": "ich-bin-bot"})
    assert res.status_code == 200
    assert res.json()["ok"] is True
    assert db.get_companies() == []                # Bot-Eintrag nicht gespeichert


def test_mail_body_lists_innovation(monkeypatch):
    monkeypatch.setenv("AGENTMAIL_API_KEY", "k")
    monkeypatch.setenv("AGENTMAIL_INBOX", "bot@agentmail.to")
    monkeypatch.setenv("MAIL_TO", "to@x.de")
    sent = {}

    class FakeResp:
        status_code = 200

    def fake_post(url, **kw):
        sent["url"] = url
        sent["json"] = kw.get("json")
        return FakeResp()

    monkeypatch.setattr(mail.httpx, "post", fake_post)
    ok = mail.send_company_notification({
        "company": "X", "email": "x@x.de", "innovation": ["Feld A", "Feld B"],
    })
    assert ok is True
    assert "bot@agentmail.to" in sent["url"]
    assert sent["json"]["to"] == ["to@x.de"]
    assert "Feld A" in sent["json"]["text"] and "Feld B" in sent["json"]["text"]


def test_mail_noop_without_config(monkeypatch):
    for var in ("AGENTMAIL_API_KEY", "AGENTMAIL_INBOX", "MAIL_TO"):
        monkeypatch.delenv(var, raising=False)
    assert mail.send_company_notification({"company": "X"}) is False
