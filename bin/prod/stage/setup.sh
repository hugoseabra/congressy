#!/usr/bin/env bash
set -ex

export DJANGO_SETTINGS_MODULE=project.settings.prod

export BASE_DIR=`python -c "
import $DJANGO_SETTINGS_MODULE as settings
print(settings.BASE_DIR)"`

export PYTHONPATH=$BASE_DIR

$BASE_DIR/bin/prod/stage/dropdb.sh
$BASE_DIR/bin/prod/stage/dropdb.sh
$BASE_DIR/bin/prod/stage/dropuser.sh
$BASE_DIR/bin/prod/createuser.sh
$BASE_DIR/bin/prod/createdb.sh

python $BASE_DIR/manage.py migrate

# Importando fixtures
python $BASE_DIR/manage.py loaddata 00_admin_user
