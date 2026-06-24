"""Adapter wfk — Cleaning Technology Institute e. V.

Terminseite listet Veranstaltungen als Absätze:
  <p><strong>09. – 11.09.2026</strong><br><a href="…flyer.pdf">Workshop „…"</a></p>
Datum ist ein Bereich; Start = führender Tag, Monat/Jahr aus dem vollen Enddatum.
"""
from __future__ import annotations

import re

from selectolax.parser import HTMLParser

from scraper.adapters.base import get_html
from scraper.model import Event

BASE = "https://wfk.de"
URL = BASE + "/transfer/seminare-workshops-konferenzen/"

_FULL = re.compile(r"(\d{1,2})\.(\d{1,2})\.(\d{4})")
_LEAD = re.compile(r"^\s*(\d{1,2})\.\s*[–—-]")


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("­", "")).strip()


def _parse_range(text: str) -> tuple[str | None, str | None]:
    """'09. – 11.09.2026' -> ('2026-09-09','2026-09-11'); '11.09.2026' -> (single, None)."""
    full = _FULL.search(text)
    if not full:
        return None, None
    d2, mo, y = int(full.group(1)), int(full.group(2)), int(full.group(3))
    end = f"{y:04d}-{mo:02d}-{d2:02d}"
    lead = _LEAD.search(text)
    if lead:
        d1 = int(lead.group(1))
        start = f"{y:04d}-{mo:02d}-{d1:02d}"
        return start, end
    return end, None


class WfkAdapter:
    institute = "wfk Cleaning Technology Institute"
    institute_id = "wfk"

    def fetch(self) -> list[Event]:
        return self.parse(get_html(URL))

    def parse(self, html: str) -> list[Event]:
        tree = HTMLParser(html)
        root = tree.css_first("div.contentunterseite") or tree
        events: list[Event] = []
        for p in root.css("p"):
            strong = p.css_first("strong")
            link = p.css_first("a")
            if strong is None or link is None:
                continue
            start, end = _parse_range(_clean(strong.text()))
            if not start:
                continue
            title = _clean(link.text())
            href = link.attributes.get("href") or ""
            if not title or not href.startswith("http"):
                continue
            try:
                events.append(Event(
                    title=title, institute=self.institute, institute_id=self.institute_id,
                    start=start, end=end if end and end != start else None,
                    location="Krefeld", url=href,
                ))
            except ValueError:
                continue
        return events
