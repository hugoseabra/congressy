#!/usr/bin/env bash
set -ex

export DJANGO_SETTINGS_MODULE=project.settings.dev

#pip install -r requirements_dev.pip
#
export BASE_DIR=`python -c "
import $DJANGO_SETTINGS_MODULE as settings
print(settings.BASE_DIR)"`

export PYTHONPATH=$BASE_DIR

docker-compose -f $BASE_DIR/bin/env/docker-compose.yml down --remove-orphans
sleep 2

docker-compose -f $BASE_DIR/bin/env/docker-compose.yml up -d
sleep 5

python $BASE_DIR/manage.py migrate

# Importando fixtures
# User
python $BASE_DIR/manage.py loaddata 000_site_dev
python $BASE_DIR/manage.py loaddata 001_user

# Workflow fixtures
python $BASE_DIR/manage.py loaddata 000_workflow_user
python $BASE_DIR/manage.py loaddata 001_workflow_person
python $BASE_DIR/manage.py loaddata 002_workflow_organization
python $BASE_DIR/manage.py loaddata 003_workflow_member
python $BASE_DIR/manage.py loaddata 004_workflow_event
python $BASE_DIR/manage.py loaddata 005_workflow_info
python $BASE_DIR/manage.py loaddata 006_workflow_lot

# Removes previous media files
rm -rf $BASE_DIR/media_dev/*

# Atualizando a data dos eventos
python $BASE_DIR/bin/env/workflow/update_data.py

