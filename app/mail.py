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
    "company": "Firma", "contact": "Ansprechpartner", "email": "E-Mail",
    "phone": "Telefon", "website": "Website", "branch": "Branche",
    "interest": "Interessensgebiet / Nachricht",
}


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

    body = "Neue Unternehmens-Anfrage über Forschungstermine:\n\n" + "\n".join(
        f"{label}: {company.get(key) or '—'}" for key, label in _LABELS.items()
    )
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
