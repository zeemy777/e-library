#!/bin/sh
# Initialise schema + demo catalogue (idempotent), then serve.
set -e
cd /app/backend

PORT="${PORT:-5000}"

# On Docker Compose the database healthcheck guarantees MySQL is up. Hosts that
# provision MySQL as a separate service (Railway, Render, …) do not, so retry
# the idempotent seed until the database accepts connections.
attempt=1
until python seed_library.py; do
  if [ "$attempt" -ge 15 ]; then
    echo "Database not reachable after $attempt attempts" >&2
    exit 1
  fi
  attempt=$((attempt + 1))
  sleep 4
done

exec gunicorn \
  --bind "0.0.0.0:${PORT}" \
  --workers "${WEB_CONCURRENCY:-2}" \
  --threads "${GUNICORN_THREADS:-4}" \
  run:app
