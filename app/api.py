"""FastAPI-Dienst: öffentliche Termin-API + geschützte Admin-Oberfläche.

Auth (HTTP-Basic) macht nginx für /admin* — die App selbst ist offen, läuft aber
nur lokal (127.0.0.1). APP_BASE = öffentlicher Pfad-Präfix (z. B. /forschungstermine)
für die Form-Actions der Admin-Seite.
"""
from __future__ import annotations

import html
import os
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app import db, mail
from app.refresh import run_refresh
from scraper.fields import field_defs

BASE = os.environ.get("APP_BASE", "")
SITE_DIR = Path(__file__).resolve().parent.parent / "site"

app = FastAPI(title="Forschungstermine")


@app.on_event("startup")
def _startup() -> None:
    db.init_db()


@app.get("/api/events")
def api_events() -> JSONResponse:
    events = db.get_events()
    return JSONResponse({
        "generated_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "count": len(events),
        "fields": field_defs(),
        "events": events,
    })


@app.post("/api/companies")
def api_companies(
    company: str = Form(...),
    first_name: str = Form(""),
    last_name: str = Form(""),
    email: str = Form(""),
    website: str = Form(""),
    request_type: str = Form(""),
    company_desc: str = Form(""),
    anonymous: str = Form(""),
    challenge_desc: str = Form(""),
    innovation: list[str] = Form(default=[]),
    newsletter: str = Form(""),
    association: str = Form(""),
    hp: str = Form(""),
) -> JSONResponse:
    """Öffentliche Pitch-&-Connect-Anfrage entgegennehmen."""
    if hp.strip():  # Honeypot gefüllt -> Bot; still schlucken.
        return JSONResponse({"ok": True})
    if not company.strip() or not email.strip():
        return JSONResponse({"ok": False, "error": "Unternehmen und E-Mail sind Pflichtfelder."},
                            status_code=422)
    data = {"company": company, "first_name": first_name, "last_name": last_name,
            "email": email, "website": website, "request_type": request_type,
            "company_desc": company_desc, "anonymous": anonymous,
            "challenge_desc": challenge_desc, "innovation": innovation,
            "newsletter": newsletter, "association": association}
    db.add_company(data)
    mail.send_company_notification(data)
    return JSONResponse({"ok": True})


@app.post("/admin/refresh")
def admin_refresh() -> RedirectResponse:
    summary = run_refresh()
    msg = (f"Aktualisiert: {summary['structured']} Termine geprüft, "
           f"{summary['new_pending']} neue KI-Vorschläge, {summary['live_total']} live.")
    return RedirectResponse(f"{BASE}/admin?msg={html.escape(msg)}", status_code=303)


@app.post("/admin/approve")
def admin_approve(id: str = Form(...)) -> RedirectResponse:
    db.approve(id)
    return RedirectResponse(f"{BASE}/admin", status_code=303)


@app.post("/admin/reject")
def admin_reject(id: str = Form(...)) -> RedirectResponse:
    db.reject(id)
    return RedirectResponse(f"{BASE}/admin", status_code=303)


@app.get("/admin", response_class=HTMLResponse)
def admin_page(msg: str = "") -> HTMLResponse:
    pending = db.get_pending()
    live = db.get_events()
    companies = db.get_companies()
    return HTMLResponse(_render_admin(pending, live, companies, msg))


def _esc(s) -> str:
    return html.escape(str(s or ""))


def _render_companies(companies: list[dict]) -> str:
    if not companies:
        return '<tr><td colspan="4" class="empty">Noch keine Anfragen.</td></tr>'
    rows = ""
    for c in companies:
        when = _esc((c.get("created_at") or "")[:16].replace("T", " "))
        person = " ".join(filter(None, [c.get("first_name"), c.get("last_name")]))
        anon = ' <span class="tag">anonym</span>' if (c.get("anonymous") == "Ja") else ""
        who = f'<b>{_esc(c.get("company"))}</b>{anon}'
        if person:
            who += f'<br><span class="meta">{_esc(person)}</span>'

        links = ""
        if c.get("email"):
            links += f'<a href="mailto:{_esc(c["email"])}">{_esc(c["email"])}</a>'
        if c.get("website"):
            links += f'<br><a href="{_esc(c["website"])}" target="_blank" rel="noopener">Website ↗</a>'

        parts = []
        if c.get("request_type"):
            parts.append(f'<div><b>Anliegen:</b> {_esc(c["request_type"])}</div>')
        if c.get("company_desc"):
            parts.append(f'<div><b>Unternehmen:</b> {_esc(c["company_desc"])}</div>')
        if c.get("challenge_desc"):
            parts.append(f'<div><b>Herausforderung:</b> {_esc(c["challenge_desc"])}</div>')
        innov = c.get("innovation") or []
        if innov:
            tags = "".join(f'<span class="tag">{_esc(i)}</span>' for i in innov)
            parts.append(f'<div class="tags">{tags}</div>')
        meta = []
        if c.get("newsletter"):
            meta.append(f'Newsletter: {_esc(c["newsletter"])}')
        if c.get("association"):
            meta.append(_esc(c["association"]))
        if meta:
            parts.append(f'<div class="meta">{" · ".join(meta)}</div>')

        rows += f"""
        <tr>
          <td class="d">{when}</td>
          <td>{who}</td>
          <td>{links or '—'}</td>
          <td class="details">{"".join(parts) or '—'}</td>
        </tr>"""
    return rows


def _render_admin(pending: list[dict], live: list[dict], companies: list[dict], msg: str) -> str:
    rows = ""
    for ev in pending:
        conf = ev.get("confidence")
        conf_txt = f"{round(conf * 100)} %" if isinstance(conf, (int, float)) else "—"
        rows += f"""
        <tr>
          <td class="d">{_esc(ev['start'])}</td>
          <td><b>{_esc(ev['title'])}</b><br><span class="meta">{_esc(ev['institute'])}
              · {_esc(ev.get('kind') or '')} · {_esc(ev.get('location') or '')}</span>
              <br><a href="{_esc(ev['url'])}" target="_blank" rel="noopener">Quelle ↗</a></td>
          <td class="c">{conf_txt}</td>
          <td class="act">
            <form method="post" action="{BASE}/admin/approve"><input type="hidden" name="id" value="{_esc(ev['id'])}"><button class="ok">Freigeben</button></form>
            <form method="post" action="{BASE}/admin/reject"><input type="hidden" name="id" value="{_esc(ev['id'])}"><button class="no">Verwerfen</button></form>
          </td>
        </tr>"""
    if not pending:
        rows = '<tr><td colspan="4" class="empty">Keine offenen KI-Vorschläge.</td></tr>'

    return f"""<!DOCTYPE html><html lang="de"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Admin · Forschungstermine</title>
<link href="https://fonts.googleapis.com/css2?family=Unbounded:wght@400;600;700&family=Figtree:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
:root{{--navy:#1a3a5c;--navy-mid:#0f2540;--cyan:#38bcd4;--cyan-dk:#1f98b0;--magenta:#d94fa0;--green:#7abe44;--muted:#6b7a85;--border:rgba(26,58,92,.12)}}
*{{box-sizing:border-box}}body{{font-family:Figtree,sans-serif;color:var(--navy);background:#faf9f7;margin:0;padding:2.5rem 5vw}}
h1{{font-family:Unbounded,sans-serif;font-weight:700;color:var(--navy-mid);font-size:1.6rem}}
.sub{{color:var(--muted);margin:.3rem 0 1.5rem}}
.bar{{display:flex;align-items:center;gap:1rem;flex-wrap:wrap;margin-bottom:1.5rem}}
.refresh{{font-family:Unbounded,sans-serif;font-size:.72rem;font-weight:600;letter-spacing:.05em;text-transform:uppercase;background:var(--navy-mid);color:#fff;border:0;border-radius:.4rem;padding:.85rem 1.8rem;cursor:pointer}}
.refresh:hover{{background:var(--navy)}}
.msg{{background:rgba(56,188,212,.12);border:1px solid var(--cyan);border-radius:.4rem;padding:.6rem 1rem;color:var(--cyan-dk);font-size:.9rem}}
h2{{font-family:Unbounded,sans-serif;font-size:.7rem;letter-spacing:.14em;text-transform:uppercase;color:var(--cyan);margin:2rem 0 .8rem}}
table{{width:100%;border-collapse:collapse;background:#fff;border:1px solid var(--border);border-radius:.6rem;overflow:hidden}}
td{{padding:.9rem 1rem;border-top:1px solid var(--border);vertical-align:top;font-size:.9rem}}
td.d{{font-family:Unbounded,sans-serif;font-weight:600;white-space:nowrap;color:var(--navy-mid)}}
td.c{{text-align:center;color:var(--muted)}}.meta{{color:var(--muted);font-size:.8rem}}
a{{color:var(--cyan-dk)}}.act{{display:flex;gap:.5rem;white-space:nowrap}}
.act button{{font-family:Figtree;font-weight:600;font-size:.8rem;border:0;border-radius:.3rem;padding:.5rem .9rem;cursor:pointer}}
.ok{{background:var(--green);color:#fff}}.no{{background:#fff;border:1px solid var(--border)!important;color:var(--muted)}}
.empty{{text-align:center;color:var(--muted);padding:2rem}}
.count{{color:var(--muted);font-size:.85rem}}
.details div{{margin-bottom:.35rem;font-size:.85rem}}
.details b{{color:var(--navy-mid)}}
.tags{{display:flex;flex-wrap:wrap;gap:.3rem;margin-top:.2rem}}
.tag{{font-size:.68rem;color:var(--cyan-dk);background:rgba(56,188,212,.1);
  border:1px solid rgba(56,188,212,.3);border-radius:2rem;padding:.12rem .55rem}}
</style></head><body>
<h1>Forschungstermine · Admin</h1>
<p class="sub">Termine serverseitig aktualisieren und KI-Vorschläge freigeben.</p>
<div class="bar">
  <form method="post" action="{BASE}/admin/refresh"><button class="refresh">↻ Jetzt aktualisieren</button></form>
  <span class="count">{len(live)} Termine live · {len(pending)} Vorschläge offen</span>
</div>
{f'<div class="msg">{_esc(msg)}</div>' if msg else ''}
<h2>KI-Vorschläge zur Freigabe</h2>
<table><tbody>{rows}</tbody></table>
<h2>Unternehmens-Anfragen ({len(companies)})</h2>
<table><tbody>{_render_companies(companies)}</tbody></table>
</body></html>"""


# Statisches Frontend zuletzt mounten (lokaler Test/Einzeldienst-Betrieb).
# In Produktion serviert nginx die statischen Dateien direkt; dieser Mount
# wird dann für /api und /admin nicht benötigt, stört aber nicht.
if SITE_DIR.exists():
    app.mount("/", StaticFiles(directory=str(SITE_DIR), html=True), name="site")
