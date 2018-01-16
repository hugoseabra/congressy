#!/usr/bin/env bash
set -ex

export DJANGO_SETTINGS_MODULE=project.settings.dev

export BASE_DIR=`python -c "
import $DJANGO_SETTINGS_MODULE as settings
print(settings.BASE_DIR)"`

export PYTHONPATH=$BASE_DIR

docker-compose -f $BASE_DIR/bin/dev/docker-compose.yml up -d
sleep 5
$BASE_DIR/bin/dev/dropdb.sh
$BASE_DIR/bin/dev/dropdb_test.sh
$BASE_DIR/bin/dev/dropuser.sh
$BASE_DIR/bin/dev/createuser.sh
$BASE_DIR/bin/dev/createdb.sh

python $BASE_DIR/manage.py migrate

# Importando fixtures
# User
python $BASE_DIR/manage.py loaddata 000_site_dev
python $BASE_DIR/manage.py loaddata 001_user

## gatheros_event
python $BASE_DIR/manage.py loaddata 005_user 006_person 007_organization 008_member 009_place
python $BASE_DIR/manage.py loaddata 010_event 011_info
python $BASE_DIR/manage.py loaddata 012_invitation

## gatheros_subscription
python $BASE_DIR/manage.py loaddata 006_lot
#python $BASE_DIR/manage.py loaddata 006_lot 007_subscription
#python $BASE_DIR/manage.py loaddata 008_answer

# Atualizando a data dos eventos
python $BASE_DIR/bin/dev/update_data.py
