# Forschungstermine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eine deployte, statische Web-Plattform, die Veranstaltungen deutscher Textilforschungsinstitute per Cron-Scraper einsammelt und im Elegant-Look als Liste + Kalender + Detailseite zeigt.

**Architecture:** Python-Scraper (Cron, 1×/Tag) mit einem Adapter pro Institut → schreibt `site/data/events.json` → statische Seite (HTML/CSS/JS) rendert daraus Liste/Kalender/Detail → nginx serviert unter `ki-textil-mode.de/forschungstermine/`.

**Tech Stack:** Python 3 (httpx, selectolax), Vanilla JS/HTML/CSS, nginx (statisch), Cron, GitHub (Org `textil-mode`), Hostinger VPS.

---

## File Structure

```
web-forschungstermine/
├─ scraper/
│  ├─ __init__.py
│  ├─ model.py          # Event-Dataclass + Normalisierung/Validierung
│  ├─ registry.py       # Liste aller aktiven Adapter
│  ├─ build.py          # CLI: alle Adapter laufen lassen → events.json
│  └─ adapters/
│     ├─ __init__.py
│     ├─ base.py        # Adapter-Protokoll + Helfer (fetch, parse_date)
│     ├─ ditf.py
│     ├─ ita_aachen.py
│     ├─ hohenstein.py
│     ├─ stfi.py
│     └─ itm_dresden.py
├─ tests/
│  ├─ test_model.py
│  ├─ test_build.py
│  └─ fixtures/         # gespeicherte HTML-Schnipsel je Institut
├─ site/
│  ├─ index.html        # Liste + Kalender (Umschalter)
│  ├─ event.html        # Detailseite (?id=)
│  ├─ assets/style.css  # Elegant-Look
│  ├─ assets/app.js     # Rendering Liste/Kalender
│  ├─ assets/event.js   # Rendering Detail
│  └─ data/events.json  # vom Scraper erzeugt (im Repo: Beispiel zum lokalen Test)
├─ requirements.txt
├─ run-scraper.sh       # Cron-Entrypoint auf dem VPS
└─ README.md
```

---

## Task 1: Projekt-Repo anlegen (Konvention)

**Files:** ganzes Repo via Tooling.

- [ ] **Step 1:** Repo im Standard anlegen:
  `pwsh _uebersicht/new-project.ps1 -name "Forschungstermine" -slug web-forschungstermine -gruppe web -zweck "Zentrale Termin-Plattform der Textilforschungsinstitute"`
- [ ] **Step 2:** Repo lokal klonen (nicht von H: entwickeln); Spec/Plan aus `docs/superpowers/` mit ins Repo übernehmen.
- [ ] **Step 3:** `requirements.txt` (`httpx`, `selectolax`, `pytest`) + `.gitignore` (`__pycache__`, `.venv`) anlegen, committen.

## Task 2: Event-Datenmodell (TDD)

**Files:** Create `scraper/model.py`, Test `tests/test_model.py`.

- [ ] **Step 1: Failing test** — `Event.normalize()` macht aus Rohwerten ein valides Objekt und erzeugt stabile `id`:

```python
from scraper.model import Event

def test_event_id_is_stable_slug():
    e = Event(title="Kolloquium: Faserverbund", institute="DITF Denkendorf",
              institute_id="ditf", start="2026-09-12", url="https://x/y")
    assert e.id == "ditf-2026-09-12-kolloquium-faserverbund"

def test_event_requires_title_and_start():
    import pytest
    with pytest.raises(ValueError):
        Event(title="", institute="DITF", institute_id="ditf", start="2026-09-12", url="https://x")
```

- [ ] **Step 2:** Run `pytest tests/test_model.py -v` → FAIL.
- [ ] **Step 3:** `Event` als dataclass implementieren: Pflichtfelder prüfen (`title`, `start`, `url`), `id` aus `institute_id` + ISO-Datum + slugifiziertem Titel (lowercase, `[^a-z0-9]+`→`-`, gekürzt). Optional: `end, kind, location, online, description`. Methode `to_dict()`.
- [ ] **Step 4:** Run `pytest tests/test_model.py -v` → PASS.
- [ ] **Step 5:** Commit `feat: Event-Datenmodell mit stabiler ID`.

## Task 3: Adapter-Basis (TDD)

**Files:** Create `scraper/adapters/base.py`, Test ergänzt `tests/test_model.py` oder neu `tests/test_base.py`.

- [ ] **Step 1: Failing test** — `parse_german_date("12. September 2026") == "2026-09-12"` und Helfer `fetch(url)` existiert (mockbar).
- [ ] **Step 2:** Run → FAIL.
- [ ] **Step 3:** In `base.py`: `Adapter`-Protokoll (`institute`, `institute_id`, `fetch() -> list[Event]`), `parse_german_date()` (Monatsnamen-Map), `get_html(url)` via httpx mit Timeout + User-Agent.
- [ ] **Step 4:** Run → PASS.
- [ ] **Step 5:** Commit `feat: Adapter-Basis + deutsche Datumsparser`.

## Task 4: Erster echter Adapter — DITF (gegen Fixture)

**Files:** Create `scraper/adapters/ditf.py`, `tests/fixtures/ditf.html`, Test `tests/test_ditf.py`.

- [ ] **Step 1:** Echte Terminseite des DITF live aufrufen (firecrawl/WebFetch), HTML-Schnipsel der Terminliste als `tests/fixtures/ditf.html` speichern.
- [ ] **Step 2: Failing test** — `DitfAdapter().parse(open(fixture).read())` liefert ≥1 Event mit korrektem `title/start/url`.
- [ ] **Step 3:** Run → FAIL.
- [ ] **Step 4:** Adapter implementieren: `parse(html)` mit selectolax-Selektoren gegen die echte Struktur; `fetch()` = `get_html(url)` → `parse`.
- [ ] **Step 5:** Run → PASS.
- [ ] **Step 6:** Commit `feat: DITF-Adapter`.

## Task 5: Weitere Adapter — ITA Aachen, Hohenstein, STFI, ITM Dresden

Pro Institut identisch zu Task 4 (eigene Fixture, eigener Test, eigener Adapter). Finale Institutsauswahl nach Sichtung der jeweiligen Terminseite; falls eine Seite keine maschinenlesbare Terminliste hat, durch ein anderes der ~16 Institute ersetzen und im README vermerken.

- [ ] ITA Aachen → `ita_aachen.py` (+ Fixture, Test, Commit)
- [ ] Hohenstein → `hohenstein.py` (+ Fixture, Test, Commit)
- [ ] STFI Chemnitz → `stfi.py` (+ Fixture, Test, Commit)
- [ ] ITM/TU Dresden → `itm_dresden.py` (+ Fixture, Test, Commit)

## Task 6: Registry + Build (TDD)

**Files:** Create `scraper/registry.py`, `scraper/build.py`, Test `tests/test_build.py`.

- [ ] **Step 1: Failing test** — `build_events([FakeAdapterA, FakeAdapterB])` führt zusammen, filtert Vergangenes (Stichtag injizierbar), sortiert nach `start`, dedupliziert per `id`; ein Adapter, der wirft, wird übersprungen (Ergebnis enthält die anderen).
- [ ] **Step 2:** Run → FAIL.
- [ ] **Step 3:** `registry.py` = `ACTIVE_ADAPTERS = [Ditf(), ...]`. `build.py`: `build_events(adapters, today=...)` → robust (try/except je Adapter, Logging), `main()` schreibt `site/data/events.json` mit `generated_at`.
- [ ] **Step 4:** Run → PASS.
- [ ] **Step 5:** Echtlauf `python -m scraper.build`, erzeugte `events.json` sichten. Commit `feat: Build-Pipeline schreibt events.json`.

## Task 7: Statische Seite — Liste + Kalender

**Files:** Create `site/index.html`, `site/assets/style.css`, `site/assets/app.js`.

- [ ] **Step 1:** `style.css` mit den Elegant-Tokens aus der Spec (aus dem abgenommenen Mockup übernehmen).
- [ ] **Step 2:** `index.html` Grundgerüst: Header (`❦`, Lede), Umschalter Liste/Kalender, zwei Container.
- [ ] **Step 3:** `app.js`: `fetch('data/events.json')`; **Liste** nach Monat gruppieren, Datum-Spalte + Instituts-Label + Art + Ort/Online, jede Zeile verlinkt auf `event.html?id=`; **Kalender** als Monatsraster, Tage mit Terminen markiert + klickbar. Umschalter via Buttons.
- [ ] **Step 4:** Lokal mit `python -m http.server` in `site/` öffnen, beide Ansichten gegen echte `events.json` prüfen.
- [ ] **Step 5:** Commit `feat: Liste + Kalender`.

## Task 8: Detailseite

**Files:** Create `site/event.html`, `site/assets/event.js`.

- [ ] **Step 1:** `event.html` im Elegant-Look (Titel, Institut, Datum, Art, Ort/Online, Beschreibung, Button „Zur Original-Seite", Zurück-Link).
- [ ] **Step 2:** `event.js`: `id` aus Query lesen, passenden Termin aus `events.json` suchen, rendern; unbekannte `id` → freundlicher Hinweis + Link zur Übersicht.
- [ ] **Step 3:** Lokal mehrere `?id=` testen (gültig + ungültig). Commit `feat: Detailseite`.

## Task 9: Cron-Entrypoint + README

**Files:** Create `run-scraper.sh`, `README.md`.

- [ ] **Step 1:** `run-scraper.sh`: venv aktivieren → `python -m scraper.build` → Exit-Code/Log. Idempotent, vom Repo-Root lauffähig.
- [ ] **Step 2:** `README.md`: Setup, lokaler Lauf, Adapter hinzufügen, Liste aktiver/offener Institute (welche der ~16 laufen, welche fehlen).
- [ ] **Step 3:** Commit `docs: README + Cron-Entrypoint`.

## Task 10: Deploy + Hosting

**Files:** nginx-Config auf VPS, Cron-Eintrag.

- [ ] **Step 1:** `deploy-hostinger`-Skill nutzen: Repo auf VPS bereitstellen, `site/` unter `location /forschungstermine/` in nginx (Backup → Änderung → `nginx -t` → reload → `curl -sI`).
- [ ] **Step 2:** Python-Umgebung auf VPS einrichten (venv + `requirements.txt`).
- [ ] **Step 3:** Cron `0 3 * * *  /pfad/run-scraper.sh` → schreibt `events.json` in das von nginx servierte `site/data/`.
- [ ] **Step 4:** Smoke-Test: `https://ki-textil-mode.de/forschungstermine/` lädt, Liste/Kalender/Detail funktionieren; ein Cron-Lauf aktualisiert die Daten.
- [ ] **Step 5:** Übersicht fortschreiben: `pwsh _uebersicht/log-fortschritt.ps1 -slug web-forschungstermine -typ deploy -titel "Live" -detail "Plattform unter /forschungstermine/ live, N Institute aktiv" -status live`.

---

## Self-Review

- **Spec coverage:** Zweck/Zielgruppe → Task 7/8 (öffentliche Liste+Detail). Scraping/Adapter → Task 3–6. MVP 3–5 Adapter → Task 4–5. Datenmodell → Task 2. Design Elegant → Task 7/8. Liste+Kalender → Task 7. Detail+Link → Task 8. GitHub-Konvention → Task 1. Deploy/Hosting/Cron → Task 9–10. Übersicht-Pflege → Task 10. YAGNI-Ausschlüsse: keine Tasks dafür (korrekt). Alle Spec-Punkte abgedeckt.
- **Placeholder-Scan:** Parser-Selektoren bewusst erst gegen echte Fixtures (Task 4/5) — kein erfundener Code. Sonst keine TBDs.
- **Typkonsistenz:** `Event`(Task 2) → `to_dict()` in Build(Task 6) → Felder in `app.js`/`event.js`(Task 7/8) identisch (`id,title,institute,start,end,kind,location,online,url,description`). `fetch()`/`parse()` einheitlich in Adapter-Basis(Task 3) und Adaptern(Task 4/5).
