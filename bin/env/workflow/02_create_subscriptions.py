# noinspection PyPep8
import django

django.setup()

from gatheros_event.models import Event, Person
from gatheros_subscription.models import Subscription
from django.db.models import Q

all_persons = Person.objects.all()[0:5]

queryset = Event.objects.all()
events = queryset.filter(Q(name__icontains='lotado') | Q(name__icontains='Lotado'))

for event in events:

    event_lots = event.lots.all()
    event_lots_size = event.lots.count()

    lot = None

    if event_lots_size > 1:
        for event_lot in event_lots:
            if "lotado" in event_lot.name.lower():
                lot = event_lot
                break
    else:
        lot = event_lots.first()

    if lot is None:
        raise Exception('Lot is None.')

    for person in all_persons:
        Subscription.objects.create(
            person=person,
            event=event,
            lot=lot,
            origin=Subscription.DEVICE_ORIGIN_WEB,
            created_by=1,
            completed=True,
        )
