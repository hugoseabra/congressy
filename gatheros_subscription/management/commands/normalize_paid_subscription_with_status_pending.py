from django.core.management.base import BaseCommand

from gatheros_subscription.models import Subscription
from payment.models import Transaction


class Command(BaseCommand):
    help = 'Atualiza as inscrições pagas mas que ainda constam como pendentes.'

    def handle(self, *args, **options):
        subscriptions = Subscription.objects.filter(
            status=Subscription.AWAITING_STATUS,
            transactions__status=Transaction.PAID,
        ).order_by('event__created', 'created')

        self.stdout.write(self.style.SUCCESS(
            'Encontradas {} inscrições pagas mas que ainda constam como '
            'pendentes.'.format(subscriptions.count())
        ))

        for subscription in subscriptions:
            self._print_subscription(subscription)
            subscription.status = Subscription.CONFIRMED_STATUS
            subscription.save()

    def _print_subscription(self, subscription: Subscription):
        self.stdout.write(self.style.SUCCESS(
            " Atualizando inscrição PK: {}\n"
            "    Evento: {}({})\n"
            "    Nome do Participante: {}\n".format(
                str(subscription.pk),
                subscription.event.name,
                subscription.event.pk,
                subscription.person.name,
            )
        ))
