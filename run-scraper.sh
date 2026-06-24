#!/usr/bin/env bash
# Cron-Entrypoint: aktualisiert die Datenbank serverseitig (strukturierte Adapter
# -> events; KI-Extraktion -> pending). Aufruf (täglich per Cron auf dem VPS):
#   /opt/web-forschungstermine/run-scraper.sh
set -euo pipefail
cd "$(dirname "$0")"

if [ -f .env ]; then set -a; . ./.env; set +a; fi
if [ -d .venv ]; then . .venv/bin/activate; fi

python -m app.refresh
echo "Datenbank aktualisiert: $(date -Is)"
