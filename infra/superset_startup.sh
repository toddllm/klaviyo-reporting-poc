#!/bin/bash
# Superset startup script for Cloud Run

# Initialize Superset
superset db upgrade
superset fab create-admin \
    --username admin \
    --firstname Superset \
    --lastname Admin \
    --email admin@example.com \
    --password admin

superset init

# Load examples (optional)
# superset load_examples

# Start Superset with Gunicorn
exec gunicorn \
    --bind 0.0.0.0:8080 \
    --workers 1 \
    --timeout 120 \
    --limit-request-line 0 \
    --limit-request-field_size 0 \
    "superset.app:create_app()"
