# Forschungstermine

Zentrale, öffentliche Termin-Plattform für die Veranstaltungen der deutschen
Textilforschungsinstitute (Konferenzen, Kolloquien, Tagungen, Webinare, Workshops).
Die Termine werden **automatisch per Scraper** eingesammelt und auf einer schlichten,
eleganten Seite als **Liste** und **Kalender** dargestellt; jeder Termin verlinkt auf
die Original-Seite des Instituts zur Anmeldung.

Live: **https://ki-textil-mode.de/forschungstermine/**

## Aufbau

```
scraper/            Python-Scraper (ein Adapter pro Institut) → site/data/events.json
  model.py          Event-Datenmodell (stabile ID, Validierung)
  adapters/base.py  Adapter-Protokoll + Helfer (HTTP, deutsche Datumsparser)
  adapters/*.py     je ein Institut
  registry.py       Liste der aktiven Adapter
  build.py          führt alle Adapter zusammen → events.json
site/               statische Seite (kein App-Server nötig)
  index.html        Liste (Standard) + Kalender (Umschalter)
  event.html        Detailseite je Termin (?id=)
  assets/           style.css (Elegant-Look), app.js, event.js
  data/events.json  vom Scraper erzeugt
tests/              pytest (Adapter gegen gespeicherte HTML-Fixtures)
```

## Lokal entwickeln

```bash
python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m scraper.build           # holt echte Termine → site/data/events.json
python -m http.server -d site 8099   # Seite unter http://127.0.0.1:8099
pytest -q                         # Tests
```

## Aktive Institute

| Institut | Quelle | Status |
|---|---|---|
| Hohenstein | `hohenstein.de/de/termine` | aktiv |
| DITF Denkendorf | `ditf.de/de/aktuelles/termine` | aktiv |

**Geprüft, aber (noch) nicht angebunden:**

- **STFI Chemnitz** (`stfi.de/events`): listet nur eine *Branchentermine*-Tabelle
  (fremde Events ohne Einzel-Links) — als Institutstermine ungeeignet.
- **ITA / DWI Aachen** (RWTH-CMS): Termine werden per JavaScript nachgeladen,
  im HTML nicht enthalten → erfordert Headless-Browser.
- Weitere FKT-Institute (TITV Greiz, DTNW, Faserinstitut …): keine maschinen­lesbare,
  verlinkte Terminliste an erratbarer URL gefunden.

## Neues Institut hinzufügen

1. `python scripts/fetch_fixtures.py` (URL ergänzen) → speichert HTML unter `tests/fixtures/`.
2. Adapter `scraper/adapters/<institut>.py` mit Klasse `…Adapter` (`institute`,
   `institute_id`, `fetch()`/`parse(html)`), Selektoren gegen die Fixture.
3. Test `tests/test_<institut>.py` gegen die Fixture.
4. Adapter in `scraper/registry.py` eintragen.
5. `pytest -q` und `python -m scraper.build` prüfen.

## Deploy / Betrieb

- Statische Seite unter `ki-textil-mode.de/forschungstermine/` (nginx, kein App-Server).
- `run-scraper.sh` läuft täglich per Cron auf dem VPS und schreibt `site/data/events.json`.
- Ein gebrochener Adapter legt die Seite nicht lahm: der Build überspringt ihn und
  behält die übrigen Termine.
