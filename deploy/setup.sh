#!/usr/bin/env bash
# Idempotentes Setup des FastAPI-Dienstes auf dem VPS.
# Aufruf: bash /opt/web-forschungstermine/deploy/setup.sh
set -euo pipefail
APP=/opt/web-forschungstermine
cd "$APP"

# 1. Abhängigkeiten
if [ ! -d .venv ]; then python3 -m venv .venv; fi
.venv/bin/pip install -q -r requirements.txt

# 2. .env anlegen (Key separat eintragen!)
if [ ! -f .env ]; then cp .env.example .env; echo "INFO: .env aus Vorlage erstellt — ANTHROPIC_API_KEY noch eintragen."; fi

# 3. systemd-Dienst
cp deploy/forschungstermine.service /etc/systemd/system/forschungstermine.service
systemctl daemon-reload
systemctl enable --now forschungstermine
systemctl restart forschungstermine

# 4. Erstbefüllung der Datenbank
set -a; . ./.env; set +a
.venv/bin/python -m app.refresh || true

sleep 1
echo "--- Dienststatus ---"
systemctl is-active forschungstermine
curl -s http://127.0.0.1:8095/api/events | head -c 80; echo
