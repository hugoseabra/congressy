from django.core.management.base import BaseCommand

from gatheros_subscription.models import Subscription


class Command(BaseCommand):
    help = 'Ajusta siglas de categorias da ABAC'

    cat_sigla = {
        2047: 'CON',
        2296: 'CON',
        2297: 'CON',
        2298: 'CON',
        2300: 'ADV',
        2299: 'ADV',
        2301: 'ACO',
        2302: 'ACO',
    }

    def handle(self, *args, **options):
        subs = Subscription.objects.filter(
            event_id=374
        )

        for sub in subs:

            lot_pk = sub.lot_id

            if lot_pk not in self.cat_sigla:
                continue

            sigla = self.cat_sigla[lot_pk]

            if sub.tag_info and sigla in sub.tag_info:
                continue

            if sub.tag_info is not None:
                sub.tag_info = '{} - {}'.format(sigla, sub.tag_info)
            else:
                sub.tag_info = sigla

            if len(sub.tag_info) > 16:
                raise Exception('{} mais que 16'.format(sub.pk))

            sub.save()
