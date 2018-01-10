#!/usr/bin/env bash
set -ex

export DJANGO_SETTINGS_MODULE=project.settings.prod

export BASE_DIR=`python -c "
import $DJANGO_SETTINGS_MODULE as settings
print(settings.BASE_DIR)"`

export PYTHONPATH=$BASE_DIR

echo $BASE_DIR/bin/prod/stage/dropdb.sh
$BASE_DIR/bin/prod/stage/dropdb.sh
$BASE_DIR/bin/prod/stage/dropuser.sh
