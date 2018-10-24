from django.core.management.base import BaseCommand
from django.db.transaction import atomic

from gatheros_subscription.models import Subscription
from payment.email_notifications import PaymentNotification
from payment.models import Transaction


class Command(BaseCommand):
    help = 'Atualiza as inscrições pagas mas que ainda constam como pendentes.'

    def handle(self, *args, **options):
        transactions = Transaction.objects.filter(
            subscription__status=Subscription.AWAITING_STATUS,
            status=Transaction.PAID,
        )

        self.stdout.write(self.style.SUCCESS(
            'Inscrições pagas e pendentes: {}'.format(transactions.count())
        ))

        with atomic():
            notifiers = list()
            for transaction in transactions:
                subscription = transaction.subscription

                subscription.status = Subscription.CONFIRMED_STATUS
                subscription.save()
                # Mantem referência no objeto
                transaction.subscription = subscription

                if subscription.notified is False:
                    notifiers.append(PaymentNotification(transaction))

                self._print_subscription(subscription)

            self.stdout.write(self.style.SUCCESS('Enviando vouchers ...'))

            # Notificação mudanças na inscrição para notificação correta.
            [n.notify() for n in notifiers]

        self.stdout.write(self.style.SUCCESS('Vouchers enviados com sucesso.'))

    def _print_subscription(self, subscription: Subscription):
        self.stdout.write(self.style.SUCCESS(
            " Atualizando inscrição PK: {}\n"
            "    Evento: {} ({})\n"
            "    Nome do Participante: {} (ID: {})\n"
            "    E-mail do Participante: {}\n".format(
                subscription.pk,
                subscription.event.name,
                subscription.event.pk,
                subscription.person.name,
                subscription.person.pk,
                subscription.person.email,
            )
        ))
