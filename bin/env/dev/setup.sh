#!/usr/bin/env bash
set -ex

export DJANGO_SETTINGS_MODULE=project.manage.settings.dev

pip install -r requirements_dev.pip

export BASE_DIR=`python -c "
import $DJANGO_SETTINGS_MODULE as settings
print(settings.BASE_DIR)"`

export PYTHONPATH=$BASE_DIR

docker-compose -f $BASE_DIR/bin/env/docker-compose.yml down --remove-orphans
sleep 1

docker-compose -f $BASE_DIR/bin/env/docker-compose.yml up -d
sleep 8
docker logs cgsy-postgres


# Removes previous media files
rm -rf $BASE_DIR/media/*
rm -rf $BASE_DIR/static

python $BASE_DIR/manage.py migrate

# Importando fixtures
# User
python $BASE_DIR/manage.py loaddata 000_site_dev
python $BASE_DIR/manage.py loaddata 001_user

# survey
python $BASE_DIR/manage.py loaddata 001_survey 002_question 003_option

# gatheros_event
python $BASE_DIR/manage.py loaddata 005_user 006_person 007_organization 008_member
python $BASE_DIR/manage.py loaddata 009_event
python $BASE_DIR/manage.py loaddata 010_place 011_info
python $BASE_DIR/manage.py loaddata 012_invitation
python $BASE_DIR/manage.py loaddata 013_feature_configuration 014_feature_management

# gatheros_subscription
python $BASE_DIR/manage.py loaddata 005_event_survey
python $BASE_DIR/manage.py loaddata 006_lotcategory 007_lot 008_subscription

# addon
python $BASE_DIR/manage.py loaddata 001_optional_service_type 002_optional_product_type
python $BASE_DIR/manage.py loaddata 003_theme 004_product 005_service

# Atualizando a data dos eventos
python $BASE_DIR/bin/env/dev/update_data.py

echo "OK"
