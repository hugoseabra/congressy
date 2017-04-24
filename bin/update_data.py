from datetime import timedelta, date

import django

django.setup()
from gatheros_event.models import Event
from gatheros_subscription.models import Lot

i = 0
ref_days = [-10, 10, 20, 25, 30, 45, 45, 50, 60, 70, 80]
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
