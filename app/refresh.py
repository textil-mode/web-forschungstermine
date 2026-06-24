"""Ein Refresh-Lauf: strukturierte Adapter -> events (live),
KI-Extraktion -> pending (Freigabe). Robust gegen Einzelfehler."""
from __future__ import annotations

import logging
from datetime import date, datetime

from app import db
from scraper.fields import classify

log = logging.getLogger("forschungstermine.refresh")


def _attach_fields(d: dict) -> dict:
    d["fields"] = classify(" ".join(filter(None, [d["title"], d.get("description"), d.get("kind")])))
    return d


def run_refresh(today: date | None = None, with_ki: bool = True) -> dict:
    """Führt den Lauf aus und gibt eine Zusammenfassung zurück."""
    today = today or date.today()
    db.init_db()
    from scraper.registry import ACTIVE_ADAPTERS

    structured = 0
    for adapter in ACTIVE_ADAPTERS:
        name = getattr(adapter, "institute", adapter.__class__.__name__)
        try:
            events = adapter.fetch()
        except Exception as exc:
            log.warning("Adapter %s fehlgeschlagen: %s", name, exc)
            continue
        for ev in events:
            d = ev.to_dict()
            if d["start"] < today.isoformat():
                continue
            db.upsert_event(_attach_fields(d), source="scraper")
            structured += 1
        log.info("Adapter %s: %d Termine", name, len(events))

    new_pending = 0
    if with_ki:
        try:
            from scraper.ki_extract import extract_candidates
            for cand in extract_candidates(today):
                if db.add_pending(cand, cand.get("confidence", 0.5)):
                    new_pending += 1
        except Exception as exc:
            log.warning("KI-Extraktion fehlgeschlagen: %s", exc)

    summary = {
        "ran_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "structured": structured,
        "new_pending": new_pending,
        "live_total": len(db.get_events(today)),
        "pending_total": len(db.get_pending()),
    }
    log.info("Refresh fertig: %s", summary)
    return summary


if __name__ == "__main__":
    import json
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    print(json.dumps(run_refresh(), ensure_ascii=False))
