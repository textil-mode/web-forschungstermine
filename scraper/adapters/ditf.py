"""Adapter DITF Denkendorf — https://www.ditf.de/de/aktuelles/termine

Struktur (stand 2026-06): je Termin ein `div.event.layout_teaser.upcoming`
(schema.org/Event) mit einem `<a href="…/termindetails/…">` und einem
`<p><strong>TT.MM.JJJJ: Titel</strong></p>`. Beschreibung in `div.teaser`.
"""
from __future__ import annotations

import re

from selectolax.parser import HTMLParser

from scraper.adapters.base import get_html, parse_german_date
from scraper.model import Event

BASE = "https://www.ditf.de"
URL = BASE + "/de/aktuelles/termine"

_DATE_PREFIX = re.compile(r"^[\d.\s–—/-]*:\s*")


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("­", "")).strip()


class DitfAdapter:
    institute = "DITF Denkendorf"
    institute_id = "ditf"

    def fetch(self) -> list[Event]:
        return self.parse(get_html(URL))

    def parse(self, html: str) -> list[Event]:
        tree = HTMLParser(html)
        events: list[Event] = []
        for item in tree.css("div.event.layout_teaser.upcoming"):
            link = item.css_first("a")
            strong = item.css_first("strong")
            if link is None or strong is None:
                continue
            href = link.attributes.get("href") or ""
            if not href:
                continue
            url = href if href.startswith("http") else BASE + href

            raw = _clean(strong.text())
            start = parse_german_date(raw)
            if not start:
                continue
            title = _DATE_PREFIX.sub("", raw).strip() or raw

            teaser = item.css_first(".teaser")
            description = _clean(teaser.text()) if teaser else None

            try:
                events.append(Event(
                    title=title, institute=self.institute, institute_id=self.institute_id,
                    start=start, kind=None, location="Denkendorf", url=url,
                    description=description or None,
                ))
            except ValueError:
                continue
        return events
