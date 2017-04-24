#!/usr/bin/env bash
set -ex

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

export BASE_DIR=`python -c "
import $DJANGO_SETTINGS_MODULE as settings
print(settings.BASE_DIR)"`

f=`mktemp`
f2=`mktemp`
echo "CREATE DATABASE $DBNAME WITH OWNER = $DBUSER ENCODING = 'UTF8' TABLESPACE = pg_default LC_COLLATE = 'pt_BR.UTF-8' LC_CTYPE = 'pt_BR.UTF-8' CONNECTION LIMIT = -1;" > $f
echo 'CREATE EXTENSION "unaccent";' > $f2
sudo sudo -u postgres psql < $f && sudo -u postgres psql $DBNAME < $f2 || exit 1;

# Rodando as migrações das apps
python $BASE_DIR/manage.py migrate