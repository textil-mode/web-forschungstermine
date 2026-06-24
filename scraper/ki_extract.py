"""KI-Extraktion: holt unstrukturierte Institutsseiten und lässt ein KI-Modell die
Veranstaltungen mit eindeutigem künftigem Datum als JSON herausziehen.

Anbieter: Google Gemini (kostenloser Free-Tier-Key, Env GEMINI_API_KEY).
Ergebnis sind Kandidaten (Event-Dicts), die als Vorschläge in `pending` landen.
Ohne Key oder bei Fehlern wird leer zurückgegeben (robust).
"""
from __future__ import annotations

import json
import logging
import os
import re
from datetime import date

import httpx
from selectolax.parser import HTMLParser

from scraper.fields import classify
from scraper.model import Event

log = logging.getLogger("forschungstermine.ki")

MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
UA = "Mozilla/5.0 (compatible; ForschungstermineBot/1.0; +https://ki-textil-mode.de/forschungstermine/)"

# Institute ohne maschinenlesbare Terminliste — News-/Presse-/Event-Seiten für die KI.
KI_TARGETS = [
    {"institute": "DTNW", "institute_id": "dtnw", "url": "https://www.dtnw.de/aktuelles/"},
    {"institute": "FIBRE Bremen", "institute_id": "fibre", "url": "https://www.faserinstitut.de/news/"},
    {"institute": "TITK", "institute_id": "titk", "url": "https://www.titk.de/veranstaltungen/messen/"},
    {"institute": "ITA Augsburg", "institute_id": "ita-augsburg", "url": "https://www.ita-augsburg.com/presse/"},
    {"institute": "DWI Aachen", "institute_id": "dwi", "url": "https://www.dwi.rwth-aachen.de/go/id/jmkw/"},
]

_PROMPT = """Du extrahierst Veranstaltungstermine eines Forschungsinstituts aus dem folgenden Seitentext.

Regeln:
- Nur Veranstaltungen mit EINDEUTIGEM, künftigem Datum (ab heute, {today}).
- Kein klares Datum erkennbar? -> Termin weglassen. Lieber nichts als raten.
- Gib ausschließlich ein JSON-Array zurück, sonst nichts. Leeres Array [] wenn nichts passt.
- Jedes Objekt: {{"title": str, "start": "YYYY-MM-DD", "end": "YYYY-MM-DD"|null, "kind": str|null, "location": str|null, "url": str|null, "confidence": 0.0-1.0}}
- "url": die spezifischste Detail-URL der Veranstaltung, falls im Text/Link erkennbar, sonst null.
- "confidence": wie sicher bist du, dass das ein echter künftiger Termin mit korrektem Datum ist.

Institut: {institute}
Quelle: {url}

SEITENTEXT:
{text}
"""


def _page_text(url: str) -> str:
    r = httpx.get(url, headers={"User-Agent": UA}, timeout=25, follow_redirects=True)
    r.raise_for_status()
    tree = HTMLParser(r.text)
    for tag in tree.css("script, style, nav, footer, header"):
        tag.decompose()
    main = tree.css_first("main") or tree.body or tree
    text = re.sub(r"\n{3,}", "\n\n", re.sub(r"[ \t]+", " ", main.text(separator="\n")))
    return text.strip()[:8000]


def _client():
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        log.info("KI-Extraktion übersprungen: GEMINI_API_KEY fehlt")
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=key)
        return genai.GenerativeModel(MODEL)
    except Exception as exc:  # SDK fehlt o. Ä.
        log.warning("Gemini-SDK nicht verfügbar: %s", exc)
        return None


def _extract_one(client, target: dict, today: date) -> list[dict]:
    try:
        text = _page_text(target["url"])
    except Exception as exc:
        log.warning("KI %s: Seite nicht ladbar: %s", target["institute"], exc)
        return []
    prompt = _PROMPT.format(today=today.isoformat(), institute=target["institute"],
                            url=target["url"], text=text)
    try:
        resp = client.generate_content(prompt)
        raw = (resp.text or "").strip()
    except Exception as exc:
        log.warning("KI %s: API-Fehler: %s", target["institute"], exc)
        return []

    m = re.search(r"\[.*\]", raw, re.S)
    if not m:
        return []
    try:
        items = json.loads(m.group(0))
    except json.JSONDecodeError:
        return []

    out = []
    for it in items:
        try:
            ev = Event(
                title=str(it["title"]).strip(),
                institute=target["institute"], institute_id=target["institute_id"],
                start=it["start"], end=it.get("end"), kind=it.get("kind"),
                location=it.get("location"), url=it.get("url") or target["url"],
            )
        except (KeyError, ValueError, TypeError):
            continue
        d = ev.to_dict()
        d["fields"] = classify(" ".join(filter(None, [d["title"], d.get("kind")])))
        d["confidence"] = float(it.get("confidence") or 0.5)
        out.append(d)
    return out


def extract_candidates(today: date | None = None) -> list[dict]:
    """Alle KI-Ziele abklappern; robuste Liste von Kandidaten-Dicts (mit confidence)."""
    today = today or date.today()
    client = _client()
    if client is None:
        return []
    candidates: list[dict] = []
    for target in KI_TARGETS:
        found = _extract_one(client, target, today)
        log.info("KI %s: %d Kandidaten", target["institute"], len(found))
        candidates.extend(found)
    return candidates
