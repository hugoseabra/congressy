from collections import OrderedDict

from django.core.management.base import BaseCommand

from gatheros_subscription.models import Subscription
from payment.models import Transaction


class Command(BaseCommand):
    help = 'Lista inscrições pagas mas que ainda constam como pendentes.'

    def handle(self, *args, **options):
        subs = Subscription.objects.filter(
            status=Subscription.AWAITING_STATUS,
            transactions__status=Transaction.PAID,
        ).exclude(
            event__id__in=[31, 47, 18, 56, 108]
        ).order_by('event__created', 'created')

        events = OrderedDict()

        for sub in subs:
            event = sub.event

            if event.name not in events:
                events[event.name] = {
                    'created': '{}'.format(event.created),
                    'pk': event.pk,
                    'subs': []
                }

            events[event.name]['subs'].append(sub)

        for event_name, item in events.items():
            print('Evento: {}'.format(event_name))
            print('    Date: {}'.format(item['created']))
            print('    ID: {}'.format(item['pk']))
            print('    Num subs: {}'.format(len(item['subs'])))

            for sub in item['subs']:
                transaction = sub.transactions.last()
                transaction_status = transaction.statuses.last()
                data = transaction_status.data

                print('       - Nome: {}'.format(sub.person.name))
                print('       - E-mail: {}'.format(sub.person.email))
                # print('       - Sub Created: {}'.format(sub.created))
                print('       - Sub Updated: {}'.format(sub.modified))
                print('       - Transaction Status date: {}'.format(
                    transaction_status.date_created
                ))
                # print('       - Pay with: {}'.format(transaction.type))
                # print('       - Manual: {}'.format(transaction.manual))

                if data and 'metadata' in data:
                    print('       - Version: {}'.format(
                        data['metadata']['system']['version']
                    ))
                else:
                    print('       - Version: NONE')

                print()
