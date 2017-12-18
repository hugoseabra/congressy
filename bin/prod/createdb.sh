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
print (settings.DATABASES['default']['USER'])
"`
run_psql "SELECT 1 FROM pg_database WHERE datname = '$DBNAME';" | grep -q 1 || run_psql "CREATE DATABASE $DBNAME WITH OWNER = $DBUSER ENCODING = 'UTF8' TEMPLATE = template0 TABLESPACE = pg_default LC_COLLATE = 'pt_BR.UTF-8' LC_CTYPE = 'pt_BR.UTF-8' CONNECTION LIMIT = -1;"
run_psql "SELECT * from pg_extension where extname=\"unaccent\";" | grep -q 1 || run_psql "CREATE EXTENSION \"unaccent\";"

