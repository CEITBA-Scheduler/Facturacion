#!/usr/bin/env bash

PROJECT_ROOT="$HOME/CEITBA"
PYTHON_VIRTUALENV="$PROJECT_ROOT/env3"

export DJANGO_SETTINGS_MODULE="CEITBA.settings_prod"

echo "Working in ${PROJECT_ROOT} with virtualenv ${PYTHON_VIRTUALENV}"
echo "Press enter to continue"
read $in

echo "Stopping gunicorn service..."
sudo supervisorctl stop ceitba

source "$PYTHON_VIRTUALENV/bin/activate"

cd "$PROJECT_ROOT"

pip install -q -r requirements.txt
pip install -q -r requirements-prod.txt

./manage.py migrate
./manage.py compilemessages -l es -v 0
./manage.py collectstatic -c --noinput -v0

deactivate

sudo cp -f "dist/ceitba.nginx" "/etc/nginx/sites-available/ceitba"
sudo cp -f "dist/blog.nginx" "/etc/nginx/sites-available/blog"

sudo nginx -t

sudo cp -f "dist/supervisor.conf" "/etc/supervisor/conf.d/ceitba.conf"

sudo supervisorctl reread
sudo supervisorctl update

sudo service nginx reload

sudo supervisorctl start all

echo "Done!"
