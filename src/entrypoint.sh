#!/bin/bash
set -e

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z db 5432; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

flask db init
flask db migrate
flask db upgrade
gunicorn -c gunicorn.py.ini app:app