#!/usr/bin/env bash
set -ex

export DJANGO_SETTINGS_MODULE=project.settings.prod

export BASE_DIR=`python -c "
import $DJANGO_SETTINGS_MODULE as settings
print(settings.BASE_DIR)"`

export PYTHONPATH=$BASE_DIR
$BASE_DIR/bin/prod/createuser.sh
$BASE_DIR/bin/prod/createdb.sh

python $BASE_DIR/manage.py migrate
python $BASE_DIR/manage.py loaddata 000_site
python $BASE_DIR/manage.py loaddata 001_user
python $BASE_DIR/manage.py loaddata 001_default_field
