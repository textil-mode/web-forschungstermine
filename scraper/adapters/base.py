"""Adapter-Basis: gemeinsames Protokoll + Helfer fürs Scrapen einer Institutsseite."""
from __future__ import annotations

import re
from typing import Protocol

import httpx

from scraper.model import Event

USER_AGENT = (
    "Mozilla/5.0 (compatible; ForschungstermineBot/1.0; "
    "+https://ki-textil-mode.de/forschungstermine/)"
)

_MONATE = {
    "januar": 1, "februar": 2, "märz": 3, "maerz": 3, "april": 4, "mai": 5,
    "juni": 6, "juli": 7, "august": 8, "september": 9, "oktober": 10,
    "november": 11, "dezember": 12,
    "jan": 1, "feb": 2, "mär": 3, "maer": 3, "apr": 4, "jun": 6, "jul": 7,
    "aug": 8, "sep": 9, "sept": 9, "okt": 10, "nov": 11, "dez": 12,
}


def parse_german_date(text: str) -> str | None:
    """Parst gängige deutsche Datumsformate zu ISO 'YYYY-MM-DD'.

    Unterstützt '12. September 2026', '12.09.2026', '2026-09-12'.
    Gibt None zurück, wenn nichts erkannt wird.
    """
    if not text:
        return None
    text = text.strip()

    # ISO bereits vorhanden
    m = re.search(r"\b(\d{4})-(\d{2})-(\d{2})\b", text)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"

    # 12.09.2026 oder 12.9.2026
    m = re.search(r"\b(\d{1,2})\.\s*(\d{1,2})\.\s*(\d{4})\b", text)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return f"{y:04d}-{mo:02d}-{d:02d}"

    # 12. September 2026
    m = re.search(r"\b(\d{1,2})\.?\s+([A-Za-zäöüÄÖÜ]+)\s+(\d{4})\b", text)
    if m:
        d = int(m.group(1))
        mo = _MONATE.get(m.group(2).lower())
        y = int(m.group(3))
        if mo:
            return f"{y:04d}-{mo:02d}-{d:02d}"
    return None


def get_html(url: str, timeout: float = 20.0) -> str:
    """Lädt eine Seite und gibt das HTML zurück (folgt Redirects)."""
    resp = httpx.get(
        url,
        headers={"User-Agent": USER_AGENT},
        timeout=timeout,
        follow_redirects=True,
    )
    resp.raise_for_status()
    return resp.text


class Adapter(Protocol):
    """Vertrag, den jeder Institut-Adapter erfüllt."""

    institute: str
    institute_id: str

    def fetch(self) -> list[Event]:
        """Lädt die Terminseite und liefert normalisierte Events."""
        ...
