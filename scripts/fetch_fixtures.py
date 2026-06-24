"""Hilfsskript: lädt die Terminseiten der Institute herunter und speichert sie als
Fixtures unter tests/fixtures/<name>.html. Nur für die Entwicklung der Adapter.

Aufruf: python scripts/fetch_fixtures.py
"""
from pathlib import Path

import httpx

FIX = Path(__file__).resolve().parent.parent / "tests" / "fixtures"
FIX.mkdir(parents=True, exist_ok=True)

UA = "Mozilla/5.0 (compatible; ForschungstermineBot/1.0; +https://ki-textil-mode.de/forschungstermine/)"

TARGETS = {
    "ditf": "https://www.ditf.de/de/aktuelles/termine",
    "hohenstein": "https://www.hohenstein.de/de/termine",
    "stfi": "https://www.stfi.de/aktuelles/termine",
    "ita_aachen": "https://www.ita.rwth-aachen.de/cms/ita/das-institut/~jfap/aktuelle-veranstaltungen/?showall=1&lidx=1",
}

for name, url in TARGETS.items():
    try:
        r = httpx.get(url, headers={"User-Agent": UA}, timeout=30, follow_redirects=True)
        out = FIX / f"{name}.html"
        out.write_text(r.text, encoding="utf-8")
        print(f"{name:12s} {r.status_code}  {len(r.text):>8d} bytes  -> {out.name}  ({r.url})")
    except Exception as exc:
        print(f"{name:12s} FEHLER: {exc}")
