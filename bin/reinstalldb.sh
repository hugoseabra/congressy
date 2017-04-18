#!/usr/bin/env bash
set -ex

export BASE_DIR=`python -c "
import $DJANGO_SETTINGS_MODULE as settings
print(settings.BASE_DIR)"`

$BASE_DIR/bin/dropdb.sh || exit 1;
$BASE_DIR/bin/createdb.sh || exit 1;

# Rodando demais migrações de todas as apps
python $BASE_DIR/manage.py migrate

# Importando fixtures

## django
python $BASE_DIR/manage.py loaddata 001_user

## gatheros_event
#python $BASE_DIR/manage.py loaddata 001_segment 002_subject 003_occupation 004_category 005_person
#python $BASE_DIR/manage.py loaddata 006_organization 007_member 008_place 009_event 010_info

## gatheros_subscription
#python $BASE_DIR/manage.py loaddata 001_form 002_field 003_field_option 004_lot 005_subscription 006_answer

# Atualizando a data dos eventos
python -c "
from datetime import timedelta, date
import django
django.setup()
from gatheros_event.models import Event
from gatheros_subscription.models import Lot

i = 0
ref_days = [-10, 10, 20, 25, 30]
for event in Event.objects.all():
    event.date_start = date.today() + timedelta(days=ref_days[i])
    event.date_end = date.today() + timedelta(days=ref_days[i] + 1)
    event.save()
    i += 1

i = 0
lot_ref_days = [[0, 15], [16, 22], [23, 30]]
for lot in Lot.objects.filter(event__pk=4):
    lot.date_start = date.today() + timedelta(days=lot_ref_days[i][0])
    lot.date_end = date.today() + timedelta(days=lot_ref_days[i][1])
    lot.save()
    i += 1
"