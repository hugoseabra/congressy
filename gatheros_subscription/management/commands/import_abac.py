import json
from django.core.management.base import BaseCommand
from kanu_locations.serializers import CitySerializer
from rest_framework import serializers

from gatheros_event.models import Person
from gatheros_subscription.models import Subscription, Lot


class PersonSerializer(serializers.ModelSerializer):
    city = CitySerializer(required=False)

    class Meta:
        model = Person
        fields = '__all__'


class Command(BaseCommand):
    help = 'Importas dados da abac da v2'

    def handle(self, *args, **options):
        with open('/tmp/abac.json', 'r') as f:  # writing JSON object
            subs = json.load(f)

        for sub in subs:

            try:
                Lot.objects.get(
                    event_id=374,
                    name__iexact=sub['category']
                )
            except Lot.DoesNotExist as e:
                print('Lote não existe: {}'.format(sub['category']))
                raise e

        for sub in subs:

            if sub['person']['city'] is None:
                del sub['person']['city']

            person = PersonSerializer(data=sub['person'])

            person.is_valid(raise_exception=True)

            p_instance = person.save()

            g = sub['group']
            if '- 2' in g:
                g = g.replace('- 2', '')

            p_instance.institution = g.upper()

            p_instance.save()

            lot = Lot.objects.get(
                event_id=374,
                name__iexact=sub['category']
            )

            Subscription.objects.create(
                person=p_instance,
                event_id=374,
                tag_info=sub['tag_info'],
                completed=True,
                test_subscription=False,
                lot=lot,
                created_by=0,
                status=Subscription.CONFIRMED_STATUS,
            )
