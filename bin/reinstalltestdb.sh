#!/usr/bin/env bash
set -ex

export DJANGO_SETTINGS_MODULE=project.settings.dev

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
python $BASE_DIR/manage.py loaddata 001_default_field 002_default_field_option 003_form 004_field 005_field_option
python $BASE_DIR/manage.py loaddata 006_lot 007_subscription
python $BASE_DIR/manage.py loaddata 008_answer

# Atualizando a data dos eventos
python $BASE_DIR/bin/update_data.py