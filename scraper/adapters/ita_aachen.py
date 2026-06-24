"""Adapter ITA Aachen — Institut für Textiltechnik der RWTH Aachen.

Terminseite (?showall=1) rendert eine Tabelle: je Zeile ein <td> mit Datum
("TT.MM.JJJJ - TT.MM.JJJJ") und ein <td> mit Titel-Link (a.iconless).

Hinweis: Das RWTH-CMS nutzt wechselnde `~xxxx`-Pfad-Tokens — die URL ggf. gegen
die Live-Seite gegenprüfen, falls der Adapter leer läuft.
"""
from __future__ import annotations

import re

from selectolax.parser import HTMLParser

from scraper.adapters.base import get_html
from scraper.model import Event

BASE = "https://www.ita.rwth-aachen.de"
URL = BASE + "/cms/ita/das-institut/~jfap/aktuelle-veranstaltungen/?showall=1"

_DATE = re.compile(r"(\d{1,2})\.(\d{1,2})\.(\d{4})")


def _iso(m: re.Match) -> str:
    d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
    return f"{y:04d}-{mo:02d}-{d:02d}"


class ItaAachenAdapter:
    institute = "ITA Aachen"
    institute_id = "ita-aachen"

    def fetch(self) -> list[Event]:
        return self.parse(get_html(URL))

    def parse(self, html: str) -> list[Event]:
        tree = HTMLParser(html)
        events: list[Event] = []
        for row in tree.css("table tbody tr"):
            link = row.css_first("a.iconless")
            if link is None:
                continue
            cells = row.css("td")
            if not cells:
                continue
            dates = list(_DATE.finditer(cells[0].text()))
            if not dates:
                continue
            start = _iso(dates[0])
            end = _iso(dates[-1]) if len(dates) > 1 else None

            title = re.sub(r"\s+", " ", link.text()).strip()
            href = link.attributes.get("href") or ""
            if not title or not href:
                continue
            url = href if href.startswith("http") else BASE + href

            try:
                events.append(Event(
                    title=title, institute=self.institute, institute_id=self.institute_id,
                    start=start, end=end if end and end != start else None,
                    location="Aachen", url=url,
                ))
            except ValueError:
                continue
        return events
