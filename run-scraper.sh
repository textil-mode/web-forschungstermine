#!/usr/bin/env bash
# Cron-Entrypoint: aktualisiert site/data/events.json aus den aktiven Adaptern.
# Aufruf (auf dem VPS, täglich per Cron):
#   /pfad/zu/web-forschungstermine/run-scraper.sh
set -euo pipefail
cd "$(dirname "$0")"

if [ -d .venv ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

python -m scraper.build
echo "events.json aktualisiert: $(date -Is)"
