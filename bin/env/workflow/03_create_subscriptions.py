# noinspection PyPep8
import django

django.setup()

from gatheros_event.models import Event, Person
from gatheros_subscription.models import Subscription, Lot
all_persons = Person.objects.all()[0:5]

for event in Event.objects.all():

    if "lotado" in event.name.lower():

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
            print(event.pk)
            print(event)
            for lot in event.lots.all():
                print("Lot: " + lot.name)
            break

        print("Working on event: " + str(event.pk))
        print("Working on Lot: " + str(lot.pk))

        for person in all_persons:
            print("Working on Person: " + person.name)
            # Subscription.objects.create(
            #     person=person, event=event, lot=lot, origin=Subscription.DEVICE_ORIGIN_WEB, created_by=1)

