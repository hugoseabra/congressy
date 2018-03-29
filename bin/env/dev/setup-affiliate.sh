#!/usr/bin/env bash
set -ex

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

bash $DIR/base-setup.sh

export DJANGO_SETTINGS_MODULE=project.affiliate.settings.dev

export BASE_DIR=`python -c "
import $DJANGO_SETTINGS_MODULE as settings
print(settings.BASE_DIR)"`

export PYTHONPATH=$BASE_DIR

python $BASE_DIR/manage.py migrate

# Importando fixtures
# User
python $BASE_DIR/manage.py loaddata 000_site_dev
python $BASE_DIR/manage.py loaddata 001_user

# gatheros_event
python $BASE_DIR/manage.py loaddata 005_user 006_person 007_organization 008_member
python $BASE_DIR/manage.py loaddata 009_event
python $BASE_DIR/manage.py loaddata 010_place 011_info

echo "OK"
