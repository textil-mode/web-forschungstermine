"""Adapter Hohenstein — https://www.hohenstein.de/de/termine

Struktur (stand 2026-06): je Termin ein `div.event.modulelist__item` mit
- `.event__date` → zwei innere <div> (Start, Ende) im Format TT.MM.JJJJ
- `a.headline--5` → Titel + Detail-Link
- `.modulelist__infobar--large .info` → Art (Seminar/Konferenz/Online-Seminar …)
- `.modulelist__infobar .info` → Land + Ort
"""
from __future__ import annotations

import re

from selectolax.parser import HTMLParser

from scraper.adapters.base import get_html, parse_german_date
from scraper.model import Event

BASE = "https://www.hohenstein.de"
URL = BASE + "/de/termine"


def _clean(text: str) -> str:
    text = text.replace("­", "")          # weiche Trennstriche entfernen
    return re.sub(r"\s+", " ", text).strip()


class HohensteinAdapter:
    institute = "Hohenstein"
    institute_id = "hohenstein"

    def fetch(self) -> list[Event]:
        return self.parse(get_html(URL))

    def parse(self, html: str) -> list[Event]:
        tree = HTMLParser(html)
        events: list[Event] = []
        for item in tree.css("div.event.modulelist__item"):
            link = item.css_first("a.headline--5")
            if link is None:
                continue
            title = _clean(link.text())
            href = link.attributes.get("href") or ""
            if not href:
                continue
            url = href if href.startswith("http") else BASE + href

            date_node = item.css_first(".event__date")
            if date_node is None:
                continue
            day_divs = date_node.css("div")
            start = parse_german_date(_clean(day_divs[0].text())) if day_divs else None
            end = parse_german_date(_clean(day_divs[1].text())) if len(day_divs) > 1 else None
            if not start:
                continue

            kind_node = item.css_first(".modulelist__infobar--large .info")
            kind = _clean(kind_node.text()) if kind_node else None
            online = bool(kind and "online" in kind.lower())

            # Ort: letzte .info-Zelle in der normalen Infobar (Stadt), falls vorhanden
            location = None
            infobars = item.css(".modulelist__infobar")
            if len(infobars) > 1:
                infos = [_clean(i.text()) for i in infobars[-1].css(".info")]
                infos = [i for i in infos if i]
                if infos:
                    location = infos[-1]

            try:
                events.append(Event(
                    title=title, institute=self.institute, institute_id=self.institute_id,
                    start=start, end=end if end and end != start else None,
                    kind=kind, location=location, online=online, url=url,
                ))
            except ValueError:
                continue
        return events
