# Konzept: Forschungstermine

**Datum:** 2026-06-24
**Status:** abgestimmt, bereit für Implementierungsplan
**Slug:** `web-forschungstermine` · Hosting: `https://ki-textil-mode.de/forschungstermine/`

## 1. Zweck & Zielgruppe

Öffentliche, zentrale Termin-Plattform für die Textilbranche. Mitgliedsunternehmen
und Interessierte finden hier gebündelt die Veranstaltungen der deutschen
Textilforschungsinstitute (Konferenzen, Kolloquien, Tagungen, Webinare, Workshops)
und springen von dort zur Original-Seite des jeweiligen Instituts, um sich anzumelden.
Die Plattform ist **Wegweiser**, nicht Anmeldesystem.

## 2. Datenbeschaffung

**Automatisches Einsammeln per Crawler**, ein **Adapter pro Institut**.

- Jeder Adapter ist eine kleine, isolierte Funktion, die genau eine Institutsseite
  kennt und eine Liste normalisierter Termin-Objekte zurückgibt.
- Bricht ein Adapter (Relaunch der Institutsseite), fallen nur dessen Termine aus –
  die übrigen laufen weiter. Fehler werden geloggt, nicht still verschluckt.
- **MVP-Datenstand:** Launch mit **3–5 Adaptern** auf Echtdaten; weitere Institute
  werden schrittweise als Adapter ergänzt. Keine Seed-/Dummy-Daten in Produktion –
  was nicht von einem Adapter kommt, steht (noch) nicht drin.
- **Erste Institute** (vom Umsetzer ausgewählt, große/wichtige mit gut
  scrapebaren Terminseiten – finale Auswahl im Plan): u. a. DITF Denkendorf,
  ITA Aachen, Hohenstein, STFI Chemnitz, ITM/TU Dresden.

## 3. Architektur

Bewusst schlank und wartungsarm – **kein laufender App-Server**.

```
[Cron auf VPS, 1×/Tag]
        │
        ▼
  scraper (Python)
   ├─ adapters/<institut>.py   (je 1 Institut)
   └─ build_events()           → schreibt events.json
        │
        ▼
  events.json  (statische Datendatei)
        │
        ▼
  Statische Seite (HTML/CSS/JS)
   ├─ index.html      Liste (Standard) + Kalender (Umschalter)
   └─ event.html?id=  Detailseite je Termin
        │
        ▼
  nginx  →  ki-textil-mode.de/forschungstermine/
```

### Komponenten

| Unit | Aufgabe | Schnittstelle | Abhängigkeit |
|---|---|---|---|
| `adapters/<institut>.py` | Eine Institutsseite scrapen, normalisierte Termine liefern | `fetch() -> list[Event]` | requests/httpx + Parser (z. B. selectolax/bs4) |
| `scraper/build.py` | Alle Adapter aufrufen, zusammenführen, sortieren, `events.json` schreiben | CLI: `python -m scraper.build` | adapters |
| `events.json` | Quelle der Wahrheit für die Seite | JSON-Schema (s. u.) | – |
| `site/index.html` + JS | Liste + Kalender aus `events.json` rendern | liest `events.json` per fetch | – |
| `site/event.html` + JS | Detailansicht eines Termins (per `?id=`) | liest `events.json` | – |

### Event-Datenmodell (`events.json`)

```json
{
  "generated_at": "2026-06-24T03:00:00+02:00",
  "events": [
    {
      "id": "ditf-2026-09-12-faserverbund",
      "title": "Kolloquium: Faserbasierte Verbundwerkstoffe",
      "institute": "DITF Denkendorf",
      "institute_id": "ditf",
      "start": "2026-09-12",
      "end": null,
      "kind": "Kolloquium",
      "location": "Denkendorf",
      "online": false,
      "url": "https://www.ditf.de/...",
      "description": "Kurzbeschreibung, falls auf der Quellseite vorhanden."
    }
  ]
}
```

- `id`: stabil aus Institut + Datum + Slug (für Detail-Deeplink & Dedup).
- Vergangene Termine werden beim Build herausgefiltert.

## 4. Design / Look & Feel

**Elegant dunkel** (warmer Braun-Verlauf, Bronze/Creme, kursive Cormorant-Serif,
`❦`-Ornament) – abgenommen per Vollbild-Mockup. Konkrete Tokens:

- Hintergrund `#1A0F09 → #3B2317`, Body-Text Creme `#EFE3CF`, Meta `#C9B79C`
- Akzent Rust `#C0603A`/`#D9774E`, Überschriften Bronze `#C9A063`/`#E0BC83`
- Display: Cormorant Garamond italic; Body: Cormorant 300 italic
- Ansichten: **Liste** (chronologisch, Monats-Gruppen) als Standard,
  **Kalender** (Monatsraster) als Umschalter. Detailseite je Termin mit
  Instituts-Label, Art, Ort/Online, Beschreibung, Button „Zur Original-Seite".

## 5. GitHub & Deploy

- Privates Repo in Org `textil-mode`, angelegt via `_uebersicht/new-project.ps1`
  (Slug `web-forschungstermine`, Gruppe `web`). Entwicklung auf lokaler Platte
  (Clone), nicht direkt auf H:.
- Übersicht/Cockpit-Eintrag wird nach jeder Teilaufgabe via
  `_uebersicht/log-fortschritt.ps1` fortgeschrieben.
- Deploy über `deploy-hostinger`-Skill; Cron auf dem VPS für den täglichen Scraper-Lauf.

## 6. Bewusst nicht im Scope (YAGNI)

- Keine Filter/Suche, keine Volltext-Recherche
- Keine Nutzerkonten, keine Anmeldung/Registrierung über die Plattform
- Kein iCal-/Kalender-Export
- Keine Einspeisung durch die Institute (reines Scraping)

## 7. Erfolgskriterien

1. `python -m scraper.build` erzeugt valide `events.json` aus den ersten Adaptern (echte Termine).
2. Seite rendert Liste **und** Kalender aus `events.json`; Umschalter funktioniert.
3. Detail-Deeplink (`event.html?id=…`) zeigt den richtigen Termin, Button verlinkt zur Quelle.
4. Seite ist unter `ki-textil-mode.de/forschungstermine/` erreichbar.
5. Cron aktualisiert `events.json` täglich; ein gebrochener Adapter legt die Seite nicht lahm.
