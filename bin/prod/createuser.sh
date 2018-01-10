#!/usr/bin/env bash
set -ex

export DJANGO_SETTINGS_MODULE=project.settings.prod

export BASE_DIR=`python -c "
import $DJANGO_SETTINGS_MODULE as settings
print(settings.BASE_DIR)"`

export DBHOST=`python -c "
import $DJANGO_SETTINGS_MODULE as settings
print (settings.DATABASES['default']['HOST'])
"`

run_psql() {
    psql -h $DBHOST -U postgres -c "$@"
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

run_psql "SELECT 1 FROM pg_roles WHERE rolname=$DBUSER" | grep -q 1 || run_psql "CREATE USER $DBUSER WITH PASSWORD '$DBPASS';"
run_psql "\du"
