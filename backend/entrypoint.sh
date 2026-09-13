#!/bin/sh
set -e

python /app/manage.py migrate --noinput --settings=config.settings.production

exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 2 \
    --access-logfile - \
    --error-logfile -
