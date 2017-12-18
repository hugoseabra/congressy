#!/usr/bin/env bash
set -ex

export DJANGO_SETTINGS_MODULE=project.settings.test

export BASE_DIR=`python -c "
import $DJANGO_SETTINGS_MODULE as settings
print(settings.BASE_DIR)"`

POSTGRES_CONTAINER_NAME='postgres'

run_psql() {
    docker exec -ti $POSTGRES_CONTAINER_NAME psql -U postgres -c "$@"
}

export DBNAME=`python -c "
import $DJANGO_SETTINGS_MODULE as settings
print (settings.DATABASES['default']['NAME'])
"`

export DBUSER=`python -c "
import $DJANGO_SETTINGS_MODULE as settings
print (settings.DATABASES['default']['USER'])
"`

run_psql "DROP DATABASE IF EXISTS test_$DBNAME;"
