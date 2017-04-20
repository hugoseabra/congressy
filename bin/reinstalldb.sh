#!/usr/bin/env bash
set -ex

export BASE_DIR=`python -c "
import $DJANGO_SETTINGS_MODULE as settings
print(settings.BASE_DIR)"`

export PYTHONPATH=$BASE_DIR
$BASE_DIR/bin/dropdb.sh || exit 1;
$BASE_DIR/bin/createdb.sh || exit 1;

# Rodando demais migrações de todas as apps
python $BASE_DIR/manage.py migrate

# Importando fixtures

# User
python $BASE_DIR/manage.py loaddata 001_user

## gatheros_event
#python $BASE_DIR/manage.py loaddata 001_segment 002_subject 003_occupation 004_category 005_person
#python $BASE_DIR/manage.py loaddata 006_organization 007_member 008_place 009_event 010_info

## gatheros_subscription
#python $BASE_DIR/manage.py loaddata 001_form 002_field 003_field_option 004_lot 005_subscription 006_answer

# Atualizando a data dos eventos
python $BASE_DIR/bin/update_data.py