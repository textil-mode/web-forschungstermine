"""Optionaler E-Mail-Versand bei neuen Pitch-&-Connect-Anfragen über AgentMail.

Sendet per AgentMail-REST-API, wenn AGENTMAIL_API_KEY, AGENTMAIL_INBOX und
MAIL_TO in der Umgebung stehen — sonst folgenlos (die Anfrage liegt ohnehin in
der DB). Fehler werden geschluckt, damit eine Mail-Panne nie eine Einsendung
verliert.
"""
from __future__ import annotations

import os

import httpx

_LABELS = {
    "company": "Unternehmen", "first_name": "Vorname", "last_name": "Nachname",
    "email": "E-Mail", "website": "Web-Adresse", "request_type": "Gesuch oder Inspiration",
    "company_desc": "Kurzbeschreibung Unternehmen", "anonymous": "Anonym bleiben",
    "challenge_desc": "Beschreibung der Herausforderung", "newsletter": "Newsletter",
    "association": "Textilverband",
}


def _fmt(key: str, company: dict) -> str:
    val = company.get(key)
    if isinstance(val, (list, tuple)):
        val = ", ".join(val)
    return f"{_LABELS[key]}: {val or '—'}"


def _build_body(company: dict) -> str:
    lines = [_fmt(k, company) for k in _LABELS]
    innov = company.get("innovation") or []
    if innov:
        lines.append("Innovationsfelder:\n  - " + "\n  - ".join(innov))
    return "Neue Pitch-&-Connect-Anfrage über Forschungstermine:\n\n" + "\n".join(lines)


def send_company_notification(company: dict) -> bool:
    """Benachrichtigung über eine neue Anfrage per AgentMail senden. True bei Versand."""
    api_key = os.environ.get("AGENTMAIL_API_KEY")
    inbox = os.environ.get("AGENTMAIL_INBOX")
    to = os.environ.get("MAIL_TO")
    if not (api_key and inbox and to):
        return False

    payload = {
        "to": [to],
        "subject": f"Neue Anfrage: {company.get('company') or 'Unternehmen'}",
        "text": _build_body(company),
    }
    if company.get("email"):
        payload["reply_to"] = [company["email"]]

    try:
        r = httpx.post(
            f"https://api.agentmail.to/v0/inboxes/{inbox}/messages/send",
            headers={"Authorization": f"Bearer {api_key}"},
            json=payload,
            timeout=15,
        )
        return r.status_code < 300
    except Exception:
        return False
