#!/bin/sh
set -e

echo "Apply migrations..."
python manage.py migrate

echo "Start gunicorn..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120
