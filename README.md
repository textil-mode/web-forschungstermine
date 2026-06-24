# Forschungstermine

Zentrale, öffentliche Termin-Plattform für die Veranstaltungen der deutschen
Textilforschungsinstitute (Konferenzen, Kolloquien, Tagungen, Webinare, Workshops).
Die Termine werden **automatisch per Scraper** eingesammelt und auf einer schlichten,
eleganten Seite als **Liste** und **Kalender** dargestellt; jeder Termin verlinkt auf
die Original-Seite des Instituts zur Anmeldung.

Live: **https://ki-textil-mode.de/forschungstermine/**

## Aufbau

```
scraper/            Scraper (ein Adapter pro Institut) + KI-Extraktion
  model.py          Event-Datenmodell (stabile ID, Validierung)
  fields.py         Innovationsfelder + Stichwort-Klassifizierung
  adapters/*.py     je ein Institut (DITF, ITA, STFI, wfk)
  registry.py       Liste der aktiven Adapter
  ki_extract.py     KI-Extraktion (Groq, Free Tier) für unstrukturierte Institute → Vorschläge
app/                FastAPI-Dienst + SQLite
  db.py             events (live) · pending (KI-Vorschläge) · rejected
  refresh.py        ein Lauf: Adapter → events, KI → pending (CLI: python -m app.refresh)
  api.py            GET /api/events · POST /admin/refresh · /admin · approve/reject
site/               statisches Frontend (Tex-Started-Look), liest api/events
  index.html        Liste + Kalender + Filter (Innovationsfelder, Suche)
  event.html        Detailseite je Termin (?id=)
deploy/             systemd-Unit + setup.sh für den VPS
tests/              pytest (Adapter, DB, Refresh, Felder)
```

## Backend & „Knopfdruck"-Aktualisierung

- **Serverseitig** (kein Browser-Scraping): Der FastAPI-Dienst hält die Termine in
  einer **SQLite-DB**. Die öffentliche Seite liest sie über `GET /api/events`.
- **Aktualisieren-Button** unter `/forschungstermine/admin` (HTTP-Basic-Auth) startet
  `POST /admin/refresh` → strukturierte Adapter schreiben live, KI-Vorschläge landen
  in `pending`.
- **KI-Vorschläge** der nicht scrapebaren Institute (Groq, kostenloser Free Tier,
  `GROQ_API_KEY` in `.env`) erscheinen im Admin mit **Freigeben / Verwerfen**
  (1 Klick). Freigegeben = live, Verworfen = dauerhaft weg. Ohne Key bleibt die
  KI inaktiv (sauber übersprungen).
- **Cron 03:00** ruft `python -m app.refresh` → vollautomatischer Nachtlauf.
- Deploy: `bash deploy/setup.sh` (venv, Dienst, Erstbefüllung); nginx proxyt
  `/forschungstermine/api/` (öffentlich) und `/forschungstermine/admin` (auth).

## Lokal entwickeln

```bash
python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m scraper.build           # holt echte Termine → site/data/events.json
python -m http.server -d site 8099   # Seite unter http://127.0.0.1:8099
pytest -q                         # Tests
```

## Institute

Es werden **ausschließlich** Institute aus der offiziellen t+m-Liste berücksichtigt:
<https://textil-mode.de/de/forschung/institute/> (Stand: 17 Einträge, DITF zählt 3×).

### Aktiv angebunden

| Institut | Quelle | Status |
|---|---|---|
| DITF Denkendorf | `ditf.de/de/aktuelles/termine` | aktiv |
| ITA Aachen | `ita.rwth-aachen.de/.../aktuelle-veranstaltungen/?showall=1` | aktiv |
| STFI Chemnitz | `stfi.de/events` | aktiv |
| wfk Cleaning Technology Institute | `wfk.de/transfer/seminare-workshops-konferenzen/` | aktiv |

> Hohenstein war zunächst angebunden, steht aber **nicht** auf der t+m-Liste und
> wurde daher entfernt.
>
> **STFI**: Die Detailseiten zeigen nur das Veröffentlichungsdatum, nicht das
> Eventdatum. Daher wird das Datum aus der „Branchentermine"-Tabelle gezogen und
> nur für Zeilen übernommen, die zu einer STFI-eigenen Event-Card passen (Titel-
> Abgleich) — so sind ausschließlich STFI-eigene, korrekt datierte Termine drin.

### Geprüft, (noch) nicht angebunden

- **TITV Greiz** (`titv-greiz.de/.../alle-termine-auf-einen-blick`): echte eigene
  Terminliste, liefert aber bei jedem HTTP-GET konsistent **500** (auch mit vollen
  Browser-Headern); übrige TITV-Seiten enthalten die Termine nicht statisch.
- **ITM Dresden** (TU-CMS): Terminseite hinter Shibboleth-SSO / JS → nicht ohne
  Headless-Browser bzw. Login scrapebar.
- **DWI Aachen, DTNW, FIBRE, ITA Augsburg, Kiwa TBU, TFI, TITK**: keine eigene,
  maschinenlesbare Terminliste mit konkreten künftigen Datums-Einträgen gefunden.
- **ifm (HS Hof), FTB (HS Niederrhein)**: nur zentrale Hochschul-Kalender, nicht
  institutsspezifisch → bewusst ausgelassen.

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
