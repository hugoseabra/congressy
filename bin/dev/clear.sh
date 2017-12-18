#!/usr/bin/env bash
set -ex

export DJANGO_SETTINGS_MODULE=project.settings.dev

export BASE_DIR=`python -c "
import $DJANGO_SETTINGS_MODULE as settings
print(settings.BASE_DIR)"`

export PYTHONPATH=$BASE_DIR
$BASE_DIR/bin/dev/dropdb.sh
$BASE_DIR/bin/dev/dropdb_test.sh
$BASE_DIR/bin/dev/dropuser.sh