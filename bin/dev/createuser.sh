#!/usr/bin/env bash
set -ex

export DJANGO_SETTINGS_MODULE=project.settings.dev

export BASE_DIR=`python -c "
import $DJANGO_SETTINGS_MODULE as settings
print(settings.BASE_DIR)"`

POSTGRES_CONTAINER_NAME='postgres'

run_psql() {
    docker exec -ti $POSTGRES_CONTAINER_NAME psql -U postgres -c "$@"
}

python -c "
import $DJANGO_SETTINGS_MODULE as settings
print(settings.DATABASES['default'])
"

export DBNAME=`python -c "
import $DJANGO_SETTINGS_MODULE as settings
try:
    print (settings.DATABASES['default']['NAME'])
except:
    print(settings.DATABASES['default']['TEST']['NAME'])
"`

export DBUSER=`python -c "
import $DJANGO_SETTINGS_MODULE as settings
print (settings.DATABASES['default']['USER'])
"`

export DBPASS=`python -c "
import $DJANGO_SETTINGS_MODULE as settings
print (settings.DATABASES['default']['PASSWORD'])
"`

run_psql "CREATE USER $DBUSER WITH PASSWORD '$DBPASS' SUPERUSER;"
run_psql "\du"
