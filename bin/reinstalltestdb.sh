#!/usr/bin/env bash
set -ex

export BASE_DIR=`python -c "
import $DJANGO_SETTINGS_MODULE as settings
print(settings.BASE_DIR)"`

export PYTHONPATH=$BASE_DIR
$BASE_DIR/bin/dropdb.sh || exit 1;
$BASE_DIR/bin/createdb.sh || exit 1;

# Importando fixtures
# User

# @TODO Decidir como ficará o usuário admin padrão
python $BASE_DIR/manage.py loaddata 001_user

## gatheros_event
python $BASE_DIR/manage.py loaddata 005_user 006_person 007_organization 008_member 009_place
python $BASE_DIR/manage.py loaddata 010_event 011_info
python $BASE_DIR/manage.py loaddata 012_invitation

## gatheros_subscription
python $BASE_DIR/manage.py loaddata 001_form 002_field 003_field_option
python $BASE_DIR/manage.py loaddata 004_lot 005_subscription

# Atualizando a data dos eventos
python $BASE_DIR/bin/update_data.py