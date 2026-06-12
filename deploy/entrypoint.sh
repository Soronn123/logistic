#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
while ! pg_isready -h "$DJANGO_DB_HOST" -p "$DJANGO_DB_PORT" -U "$DJANGO_DB_USER" -q; do
  sleep 1
done
echo "PostgreSQL is ready."

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Checking fixture data..."
CITY_COUNT=$(python manage.py shell -c "from apps.geo.models import City; print(City.objects.count())" 2>/dev/null | tail -1)
if [ "$CITY_COUNT" -eq 0 ] 2>/dev/null; then
  echo "Seeding data..."
  python manage.py seed_data
else
  echo "Data already seeded ($CITY_COUNT cities), skipping."
fi

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
exec gunicorn baikal.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --access-logfile - \
    --error-logfile -
