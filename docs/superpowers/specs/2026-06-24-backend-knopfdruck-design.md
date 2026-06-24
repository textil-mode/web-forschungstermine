# Konzept: Backend „Knopfdruck-Aktualisierung" + KI-Extraktion

**Datum:** 2026-06-24
**Status:** abgestimmt
**Baut auf:** der bestehenden statischen Tex-Started-Seite + den 4 Adaptern (DITF, ITA, STFI, wfk).

## 1. Ziel

Die Seite soll sich **per Knopfdruck serverseitig** nachfüllen (kein Browser-Scraping),
die Daten in einer **Datenbank** halten, und die nicht maschinenlesbaren Institute
über **KI-Extraktion mit 1-Klick-Freigabe** abdecken — ohne dass der Nutzer Termine
manuell prüft und einträgt.

## 2. Architektur

```
            nginx (ki-textil-mode.de)
   ┌───────────────┴────────────────────────┐
   │ /forschungstermine/        (statisch)   │  ← Tex-Started-Frontend (unverändert im Look)
   │ /forschungstermine/api/    (proxy)      │  ┐
   │ /forschungstermine/admin   (proxy+auth) │  ├─► FastAPI-Dienst (uvicorn, eigener Port)
   └─────────────────────────────────────────┘  ┘        │
                                                          ▼
                                                   SQLite (events.db)
                                                   ├─ events   (bestätigt, live)
                                                   └─ pending  (KI-Vorschläge)
```

- **Frontend** bleibt statisch (schnell), liest die Termine jetzt von `api/events`
  statt aus `data/events.json`. Design unverändert (Tex Started 01).
- **FastAPI-Dienst** kapselt Scraper, DB und KI; läuft als systemd-Dienst hinter nginx.
- **Auth:** HTTP-Basic über nginx für `/api/refresh` und `/admin` (ein Nutzer/Passwort,
  wie bei `/praesentationen`). `api/events` bleibt öffentlich (read-only).

## 3. Datenmodell (SQLite)

`events` (live): `id` (PK), `title, institute, institute_id, start, end, kind,
location, online, url, description, fields (JSON), source` (`scraper`|`ki`|`manual`),
`updated_at`.
`pending` (KI-Vorschläge): wie `events` + `confidence`, `created_at`. Freigabe
verschiebt einen Datensatz von `pending` → `events`; Verwerfen löscht ihn (mit
Merkliste „verworfen", damit derselbe Vorschlag nicht wiederkommt).

## 4. Komponenten

| Unit | Aufgabe |
|---|---|
| `app/db.py` | SQLite-Anbindung, Schema, Upsert/Query/Approve/Reject |
| `app/api.py` | FastAPI: `GET /api/events`, `POST /api/refresh`, `/admin`, `POST /api/approve`, `/api/reject` |
| `app/refresh.py` | Orchestriert einen Lauf: strukturierte Adapter → `events`; KI-Adapter → `pending` |
| `scraper/adapters/*` | unverändert (liefern `Event`-Objekte) |
| `scraper/ki_extract.py` | holt unstrukturierte Seiten, ruft Claude API, validiert → Kandidaten |
| `app/templates/admin.html` | Review-Liste: „Jetzt aktualisieren"-Button + Freigeben/Verwerfen je Vorschlag |

## 5. Endpoints

- `GET /api/events` (öffentlich) → bestätigte Termine als JSON (gleiche Form wie bisher
  `events.json`, inkl. `fields`-Definitionen). Frontend liest daraus.
- `POST /api/refresh` (auth) → startet einen Scrape-Lauf **serverseitig**, aktualisiert DB,
  liefert Zusammenfassung (neu/aktualisiert/neue KI-Vorschläge). Das ist der Knopf.
- `GET /admin` (auth) → HTML-Seite: Aktualisieren-Button + Liste der `pending`-Vorschläge.
- `POST /api/approve` / `POST /api/reject` (auth) → 1-Klick-Freigabe/Verwerfen.

## 6. KI-Extraktion

- Pro nicht-strukturiertem Institut (DTNW, FIBRE, DWI, ITM, ITA Augsburg, Kiwa, TFI,
  TITK, TITV, ifm, FTB): bekannte News-/Veranstaltungs-URL holen, Klartext extrahieren,
  an Claude (Modell `claude-haiku-4-5` für Kosten/Tempo) mit striktem JSON-Schema geben:
  nur Termine mit **eindeutigem künftigem Datum**; kein Datum → kein Vorschlag.
- Ergebnisse landen in `pending` (nicht live), bis der Nutzer sie freigibt.
- **API-Key:** vom VPS (vorhandener `ANTHROPIC_API_KEY` aus anderem Projekt) via Env;
  niemals im Repo.
- Robust: Bricht die KI/Extraktion für ein Institut, läuft der Rest weiter (wie Scraper).

## 7. Betrieb / Deploy

- FastAPI als **systemd-Dienst** (`uvicorn app.api:app`), eigener Port (frei zu vergeben).
- nginx: `location /forschungstermine/api/` + `/forschungstermine/admin` → `proxy_pass`
  auf den Port; `/forschungstermine/` weiter statisch (alias). Backup→`nginx -t`→reload.
- **Cron 03:00** ruft künftig `POST /api/refresh` (statt direkt das Build-Skript) →
  vollautomatischer Nachtlauf; der Button macht dasselbe on-demand.

## 8. Bewusst nicht im Scope (YAGNI)

- Keine Nutzerverwaltung/Rollen (ein Basic-Auth-Login genügt).
- Keine Bearbeitung einzelner Termine im Admin (nur Freigeben/Verwerfen).
- Kein Echtzeit-Push; die öffentliche Seite lädt beim Aufruf.

## 9. Erfolgskriterien

1. `POST /api/refresh` (Button **und** Cron) füllt die DB serverseitig; Frontend zeigt die Termine aus `api/events`.
2. Strukturierte Institute landen direkt live; KI-Vorschläge landen in `pending`.
3. `/admin` zeigt Vorschläge; Freigeben verschiebt sie nach live, Verwerfen entfernt sie dauerhaft.
4. Öffentliche Seite unverändert im Tex-Started-Look, nur datengetrieben aus der DB.
5. Ein gebrochener Adapter/KI-Lauf legt weder DB noch Seite lahm.
