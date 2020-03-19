#!/usr/bin/env bash

DATE=`date +%F_%H:%M:%S`
BACKUP_FILE="/tmp/CEITBA-BACKUP_$DATE.json"
COMPRESSED_FILE="$BACKUP_FILE.gz"

PROJECT_ROOT="/home/sebikul/CEITBA"
PYTHON_VIRTUALENV="$PROJECT_ROOT/env3"

echo "Sourcing configuration and python virtualenv..."

source "$PYTHON_VIRTUALENV/bin/activate"

export DJANGO_SETTINGS_MODULE="CEITBA.settings_prod"

echo "Creating django backup..."
${PROJECT_ROOT}/manage.py dumpdata --natural-primary --natural-foreign -o "$BACKUP_FILE" --indent 2 -e sessions -e admin

echo "Compressing file..."
gzip -c9 "$BACKUP_FILE" > "$COMPRESSED_FILE"

echo "Pushing backup file to remote host..."
<<<<<<< HEAD
scp "$COMPRESSED_FILE" sebikul.me:/home/sebi/CEITBA-BACKUPS/
=======
scp "$COMPRESSED_FILE" sebikul.me:/home/sebikul/CEITBA-BACKUPS/
>>>>>>> c5b34188a09cab9d1d8a7e8c310d6ee64756161f

echo "Done!"
