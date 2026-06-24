"""Event-Datenmodell: eine normalisierte Veranstaltung mit stabiler ID."""
from __future__ import annotations

import re
from dataclasses import dataclass, field


def slugify(text: str, maxlen: int = 50) -> str:
    """Kleinschreiben, Umlaute ersetzen, alles Nicht-Alphanumerische zu '-'."""
    text = text.lower().strip()
    umlaut = {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"}
    for k, v in umlaut.items():
        text = text.replace(k, v)
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text[:maxlen].strip("-")


@dataclass
class Event:
    """Eine Veranstaltung eines Instituts.

    Pflichtfelder: title, institute, institute_id, start (ISO YYYY-MM-DD), url.
    `id` wird stabil aus institute_id + start + Titel-Slug erzeugt.
    """

    title: str
    institute: str
    institute_id: str
    start: str
    url: str
    end: str | None = None
    kind: str | None = None
    location: str | None = None
    online: bool = False
    description: str | None = None
    id: str = field(default="", init=False)

    def __post_init__(self) -> None:
        if not self.title or not self.title.strip():
            raise ValueError("Event braucht einen Titel")
        if not self.start or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", self.start):
            raise ValueError(f"Event braucht ein ISO-Startdatum (YYYY-MM-DD), war: {self.start!r}")
        if not self.url or not self.url.startswith("http"):
            raise ValueError("Event braucht eine gültige URL")
        if not self.institute_id:
            raise ValueError("Event braucht eine institute_id")
        self.id = f"{self.institute_id}-{self.start}-{slugify(self.title)}"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "institute": self.institute,
            "institute_id": self.institute_id,
            "start": self.start,
            "end": self.end,
            "kind": self.kind,
            "location": self.location,
            "online": self.online,
            "url": self.url,
            "description": self.description,
        }
