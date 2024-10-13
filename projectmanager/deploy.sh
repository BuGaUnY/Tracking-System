#!/usr/bin/env sh
set -e

echo "Starting migration"
python manage.py migrate --noinput 
echo "Migration completed"

echo "Starting collectstatic"
python manage.py collectstatic --noinput
echo "Collectstatic completed"

pip install -r requirements.txt

python manage.py migrate