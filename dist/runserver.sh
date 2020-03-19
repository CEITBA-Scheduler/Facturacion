#!/usr/bin/env bash

PROJECT_ROOT="/home/sebikul/CEITBA"
PYTHON_VIRTUALENV="$PROJECT_ROOT/env3"

source "$PYTHON_VIRTUALENV/bin/activate"

export DJANGO_SETTINGS_MODULE=CEITBA.settings_prod

exec gunicorn --workers 2 --bind unix:/home/sebikul/CEITBA/CEITBA.sock CEITBA.wsgi:application
