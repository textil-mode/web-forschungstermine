"""Build-Pipeline: alle aktiven Adapter laufen lassen → site/data/events.json."""
from __future__ import annotations

import json
import logging
import sys
from datetime import date, datetime, timezone
from pathlib import Path

from scraper.model import Event

log = logging.getLogger("forschungstermine.build")

SITE_DATA = Path(__file__).resolve().parent.parent / "site" / "data" / "events.json"


def build_events(adapters, today: date | None = None) -> list[dict]:
    """Führt alle Adapter aus, robust gegen Einzelfehler.

    - Ein Adapter, der wirft, wird übersprungen (geloggt), die anderen laufen weiter.
    - Vergangene Termine (start < today) werden herausgefiltert.
    - Dedup über Event.id, Sortierung nach start.
    """
    today = today or date.today()
    by_id: dict[str, Event] = {}
    for adapter in adapters:
        name = getattr(adapter, "institute", adapter.__class__.__name__)
        try:
            events = adapter.fetch()
        except Exception as exc:  # ein Institut darf die ganze Seite nicht lahmlegen
            log.warning("Adapter %s fehlgeschlagen: %s", name, exc)
            continue
        for ev in events:
            if _start_date(ev.start) < today:
                continue
            by_id[ev.id] = ev
        log.info("Adapter %s: %d Termine", name, len(events))

    ordered = sorted(by_id.values(), key=lambda e: e.start)
    return [e.to_dict() for e in ordered]


def _start_date(iso: str) -> date:
    return datetime.strptime(iso, "%Y-%m-%d").date()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    from scraper.registry import ACTIVE_ADAPTERS

    events = build_events(ACTIVE_ADAPTERS)
    payload = {
        "generated_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "count": len(events),
        "events": events,
    }
    SITE_DATA.parent.mkdir(parents=True, exist_ok=True)
    SITE_DATA.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    log.info("Geschrieben: %s (%d Termine)", SITE_DATA, len(events))
    return 0


if __name__ == "__main__":
    sys.exit(main())
