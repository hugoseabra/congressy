#!/usr/bin/env bash
set -ex

export DJANGO_SETTINGS_MODULE=project.settings.prod

BASE_DIR=`python -c "
import $DJANGO_SETTINGS_MODULE as settings
print(settings.BASE_DIR)"`

DBUSER=`python -c "
import $DJANGO_SETTINGS_MODULE as settings
print (settings.DATABASES['default']['USER'])
"`

DBHOST=`python -c "
import $DJANGO_SETTINGS_MODULE as settings
print (settings.DATABASES['default']['HOST'])
"`

DBPORT=`python -c "
import $DJANGO_SETTINGS_MODULE as settings
print (settings.DATABASES['default']['PORT'])
"`

run_psql() {
    psql -h $DBHOST -p $DBPORT -U $DBUSER -c "$@"
}

python -c "
import $DJANGO_SETTINGS_MODULE as settings
print(settings.DATABASES['default'])
"

DBNAME=`python -c "
import $DJANGO_SETTINGS_MODULE as settings
try:
    print (settings.DATABASES['default']['NAME'])
except:
    print(settings.DATABASES['default']['TEST']['NAME'])
"`

DBUSER=`python -c "
import $DJANGO_SETTINGS_MODULE as settings
print (settings.DATABASES['default']['USER'])
"`

run_psql "DROP DATABASE IF EXISTS $DBNAME;"
run_psql "DROP EXTENSION IF EXISTS unaccent;"
