#!/bin/bash
set -e

echo "Running Alembic migrations..."
alembic upgrade head

echo "Starting server..."

if [ "${UVICORN_RELOAD}" = "true" ]; then
    exec uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
else
    exec uvicorn backend.main:app --host 0.0.0.0 --port 8000 \
        --workers "${UVICORN_WORKERS:-4}"
fi
