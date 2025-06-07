echo "Apply database migrations"
python manage.py migrate --noinput

echo "Collect static files"
python manage.py collectstatic --noinput

echo "Starting Gunicorn"
exec "$@"