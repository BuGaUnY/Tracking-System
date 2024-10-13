#!/usr/bin/env sh
set -e

echo "Starting migration"
python manage.py migrate --noinput 
echo "Migration completed"

echo "Starting collectstatic"
python manage.py collectstatic --noinput
echo "Collectstatic completed"

# Installing dependencies
echo "Installing dependencies"
pip install -r requirements.txt

# You don't need to run migrate again; it's already done above.
# Commenting this line
# python manage.py migrate

# Starting Gunicorn server
echo "Starting Gunicorn"
gunicorn projectmanager.wsgi:application
