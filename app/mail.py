"""Optionaler E-Mail-Versand bei neuen Unternehmens-Anfragen.

Nutzt SMTP, wenn SMTP_HOST/SMTP_USER/SMTP_PASS/MAIL_TO in der Umgebung stehen —
sonst folgenlos (die Anfrage liegt ohnehin in der DB). Fehler werden geschluckt,
damit eine Mail-Panne nie eine Einsendung verliert.
"""
from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage

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


def send_company_notification(company: dict) -> bool:
    """Benachrichtigung über eine neue Anfrage senden. True bei Versand."""
    host = os.environ.get("SMTP_HOST")
    user = os.environ.get("SMTP_USER")
    password = os.environ.get("SMTP_PASS")
    to = os.environ.get("MAIL_TO")
    if not (host and user and password and to):
        return False

    port = int(os.environ.get("SMTP_PORT", "587"))
    sender = os.environ.get("MAIL_FROM", user)

    lines = [_fmt(k, company) for k in _LABELS]
    innov = company.get("innovation") or []
    if innov:
        lines.append("Innovationsfelder:\n  - " + "\n  - ".join(innov))
    body = "Neue Pitch-&-Connect-Anfrage über Forschungstermine:\n\n" + "\n".join(lines)
    msg = EmailMessage()
    msg["Subject"] = f"Neue Anfrage: {company.get('company') or 'Unternehmen'}"
    msg["From"] = sender
    msg["To"] = to
    if company.get("email"):
        msg["Reply-To"] = company["email"]
    msg.set_content(body)

    try:
        with smtplib.SMTP(host, port, timeout=10) as srv:
            srv.starttls()
            srv.login(user, password)
            srv.send_message(msg)
        return True
    except Exception:
        return False
