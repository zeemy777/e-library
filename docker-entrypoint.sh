#!/bin/sh
# Initialise schema + demo catalogue (idempotent), then serve.
set -e
cd /app/backend
python seed_library.py
exec gunicorn --bind 0.0.0.0:5000 --workers 2 --threads 4 run:app