#!/bin/sh
set -e

echo "Starting HealthSphere Enterprise Container Initialization..."

# Run database migrations
python manage.py migrate --noinput

# Collect static assets
python manage.py collectstatic --noinput --clear || true

echo "HealthSphere production initialization complete. Executing command..."
exec "$@"
