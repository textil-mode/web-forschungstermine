"""SQLite-Speicher: bestätigte Termine (events), KI-Vorschläge (pending), Verworfene.

Schema bewusst schlank. `fields` wird als JSON-Text abgelegt, `online` als 0/1.
"""
from __future__ import annotations

import json
import os
import sqlite3
from datetime import date, datetime, timezone
from pathlib import Path

DB_PATH = Path(os.environ.get(
    "FORSCHUNGSTERMINE_DB",
    Path(__file__).resolve().parent.parent / "data" / "events.db",
))

_COLS = ["id", "title", "institute", "institute_id", "start", "end", "kind",
         "location", "online", "url", "description", "fields", "source"]


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def init_db() -> None:
    with _connect() as con:
        for table in ("events", "pending"):
            con.execute(f"""
                CREATE TABLE IF NOT EXISTS {table} (
                    id TEXT PRIMARY KEY, title TEXT, institute TEXT, institute_id TEXT,
                    start TEXT, end TEXT, kind TEXT, location TEXT, online INTEGER,
                    url TEXT, description TEXT, fields TEXT, source TEXT,
                    confidence REAL, updated_at TEXT
                )""")
        con.execute("CREATE TABLE IF NOT EXISTS rejected (id TEXT PRIMARY KEY, at TEXT)")
        con.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL, contact TEXT, email TEXT, phone TEXT,
                website TEXT, branch TEXT, interest TEXT, created_at TEXT
            )""")


def _to_row(ev: dict, source: str, confidence: float | None = None) -> dict:
    return {
        "id": ev["id"], "title": ev["title"], "institute": ev["institute"],
        "institute_id": ev["institute_id"], "start": ev["start"], "end": ev.get("end"),
        "kind": ev.get("kind"), "location": ev.get("location"),
        "online": 1 if ev.get("online") else 0, "url": ev["url"],
        "description": ev.get("description"), "fields": json.dumps(ev.get("fields") or []),
        "source": source, "confidence": confidence,
        "updated_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
    }


def _from_row(r: sqlite3.Row) -> dict:
    return {
        "id": r["id"], "title": r["title"], "institute": r["institute"],
        "institute_id": r["institute_id"], "start": r["start"], "end": r["end"],
        "kind": r["kind"], "location": r["location"], "online": bool(r["online"]),
        "url": r["url"], "description": r["description"],
        "fields": json.loads(r["fields"] or "[]"), "source": r["source"],
    }


def upsert_event(ev: dict, source: str = "scraper") -> None:
    """Bestätigten Termin in `events` einfügen/aktualisieren (PK = id)."""
    row = _to_row(ev, source)
    cols = ", ".join(row.keys())
    ph = ", ".join("?" for _ in row)
    with _connect() as con:
        con.execute(f"INSERT OR REPLACE INTO events ({cols}) VALUES ({ph})", list(row.values()))


def add_pending(ev: dict, confidence: float, source: str = "ki") -> bool:
    """KI-Vorschlag in `pending` legen — außer er ist schon live, schon vorgeschlagen
    oder bereits verworfen. Gibt True zurück, wenn neu aufgenommen."""
    with _connect() as con:
        for tbl in ("events", "pending", "rejected"):
            if con.execute(f"SELECT 1 FROM {tbl} WHERE id=?", (ev["id"],)).fetchone():
                return False
        row = _to_row(ev, source, confidence)
        cols = ", ".join(row.keys())
        ph = ", ".join("?" for _ in row)
        con.execute(f"INSERT INTO pending ({cols}) VALUES ({ph})", list(row.values()))
        return True


def get_events(today: date | None = None) -> list[dict]:
    today = (today or date.today()).isoformat()
    with _connect() as con:
        rows = con.execute(
            "SELECT * FROM events WHERE start >= ? ORDER BY start", (today,)).fetchall()
    return [_from_row(r) for r in rows]


def get_pending() -> list[dict]:
    with _connect() as con:
        rows = con.execute("SELECT * FROM pending ORDER BY start").fetchall()
    out = []
    for r in rows:
        d = _from_row(r)
        d["confidence"] = r["confidence"]
        out.append(d)
    return out


def approve(pending_id: str) -> bool:
    """Vorschlag von `pending` nach `events` verschieben."""
    with _connect() as con:
        r = con.execute("SELECT * FROM pending WHERE id=?", (pending_id,)).fetchone()
        if not r:
            return False
        keys = [k for k in r.keys()]
        cols = ", ".join(keys)
        ph = ", ".join("?" for _ in keys)
        con.execute(f"INSERT OR REPLACE INTO events ({cols}) VALUES ({ph})", [r[k] for k in keys])
        con.execute("DELETE FROM pending WHERE id=?", (pending_id,))
        return True


_COMPANY_FIELDS = ("company", "contact", "email", "phone", "website", "branch", "interest")


def add_company(data: dict) -> int:
    """Unternehmens-Anfrage speichern. Gibt die neue Zeilen-ID zurück."""
    row = {k: (str(data.get(k) or "").strip() or None) for k in _COMPANY_FIELDS}
    row["created_at"] = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    cols = ", ".join(row.keys())
    ph = ", ".join("?" for _ in row)
    with _connect() as con:
        cur = con.execute(f"INSERT INTO companies ({cols}) VALUES ({ph})", list(row.values()))
        return int(cur.lastrowid)


def get_companies() -> list[dict]:
    """Alle Anfragen, neueste zuerst."""
    with _connect() as con:
        rows = con.execute("SELECT * FROM companies ORDER BY created_at DESC, id DESC").fetchall()
    return [dict(r) for r in rows]


def reject(pending_id: str) -> bool:
    """Vorschlag verwerfen und merken, damit er nicht wiederkommt."""
    now = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    with _connect() as con:
        r = con.execute("SELECT 1 FROM pending WHERE id=?", (pending_id,)).fetchone()
        if not r:
            return False
        con.execute("DELETE FROM pending WHERE id=?", (pending_id,))
        con.execute("INSERT OR REPLACE INTO rejected (id, at) VALUES (?, ?)", (pending_id, now))
        return True
