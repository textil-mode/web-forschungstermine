"""Adapter STFI — Sächsisches Textilforschungsinstitut e. V.

Quelle: https://www.stfi.de/events

Zwei Bausteine auf der Seite:
- Event-Cards (article.uagb-post__inner-wrap): STFI-eigene Veranstaltungen mit
  Titel und Detail-Link, aber ohne maschinenlesbares Datum.
- "Branchentermine"-Tabelle: Termine mit Datum, aber ohne Einzel-Links und inkl.
  fremder Events.

Strategie: Eine Tabellenzeile gilt als STFI-Termin, wenn ihr Titel zu einer Card
passt. Datum kommt aus der Tabelle, Titel + Detail-Link aus der Card. So sind nur
STFI-eigene Termine drin, sauber datiert und verlinkt.
"""
from __future__ import annotations

import re

from selectolax.parser import HTMLParser

from scraper.adapters.base import get_html
from scraper.model import Event

BASE = "https://www.stfi.de"
URL = BASE + "/events"

_FULL = re.compile(r"(\d{1,2})\.(\d{1,2})\.(\d{4})")
_YM = re.compile(r"(\d{1,2})\.\D*?(\d{4})")
_DM = re.compile(r"\D*(\d{1,2})\.")


def _norm(s: str) -> str:
    s = s.lower().replace("­", "")
    for a, b in {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"}.items():
        s = s.replace(a, b)
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def _key(title: str) -> str:
    """Erste zwei nicht-numerischen Wörter eines Titels (für den Card↔Tabelle-Abgleich)."""
    words = [w for w in _norm(title).split() if not w.isdigit()]
    return " ".join(words[:2])


def _parse_date(text: str) -> str | None:
    """Tolerantes Parsen: '17.6.2026' oder Bereiche wie '22.-23.-10.2026' (-> Startdatum)."""
    m = _FULL.search(text)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 1 <= mo <= 12 and 1 <= d <= 31:
            return f"{y:04d}-{mo:02d}-{d:02d}"
    ym = _YM.search(text)
    dm = _DM.match(text)
    if ym and dm:
        mo, y, d = int(ym.group(1)), int(ym.group(2)), int(dm.group(1))
        if 1 <= mo <= 12 and 1 <= d <= 31:
            return f"{y:04d}-{mo:02d}-{d:02d}"
    return None


class StfiAdapter:
    institute = "STFI Chemnitz"
    institute_id = "stfi"

    def fetch(self) -> list[Event]:
        return self.parse(get_html(URL))

    def parse(self, html: str) -> list[Event]:
        tree = HTMLParser(html)

        # Cards: Titel + Detail-Link
        cards = []
        for art in tree.css("article.uagb-post__inner-wrap"):
            a = art.css_first("h5.uagb-post__title a")
            if a is None:
                continue
            title = re.sub(r"\s+", " ", a.text()).strip()
            href = a.attributes.get("href") or ""
            if title and href.startswith("http"):
                cards.append((title, href, _key(title)))

        events: list[Event] = []
        seen: set[str] = set()
        for tbl in tree.css("table"):
            for row in tbl.css("tr"):
                cells = [c.text().strip() for c in row.css("td")]
                if len(cells) < 2:
                    continue
                start = _parse_date(cells[0])
                if not start:
                    continue
                table_title = re.sub(r"\s+", " ", cells[1])
                table_norm = _norm(table_title)
                location = cells[2].strip() if len(cells) > 2 else None

                match = next((c for c in cards if c[2] and c[2] in table_norm), None)
                if not match:
                    continue  # kein STFI-eigener Termin
                title, url, _ = match
                if url in seen:
                    continue
                seen.add(url)
                try:
                    events.append(Event(
                        title=title, institute=self.institute, institute_id=self.institute_id,
                        start=start, location=location or None, url=url,
                    ))
                except ValueError:
                    continue
        return events
