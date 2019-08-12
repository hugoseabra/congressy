from datetime import datetime

from django.core.management.base import BaseCommand
from django.db.models import Count, Sum
from django.db.transaction import atomic

from gatheros_subscription.models import Subscription
from payment.models import Transaction


class Command(BaseCommand):
    help = 'Atualiza as inscrições pagas mas que ainda constam como pendentes.'

    def handle(self, *args, **options):
        now = datetime.now()

        subs = Subscription.objects.annotate(
            num_trans=Count('transactions')
        ).filter(
            status=Subscription.AWAITING_STATUS,
            origin=Subscription.DEVICE_ORIGIN_HOTSITE,
            lot__price__gt=0,
            num_trans__gt=0,
            transactions__status=Transaction.PAID,
        )

        with atomic():
            num = 0
            processed_subs = list()

            for sub in subs:
                price_to_pay = sub.lot.get_calculated_price()

                trans = sub.transactions.aggregate(total_amount=Sum('amount'))

                paid = trans['total_amount'] or 0

                # Se não há pagamentos, tudo certo.
                # Se há pagamento e valor pago é menor do que o que se tem
                # de pagar
                if not paid and paid < price_to_pay:
                    continue

                # Se há pagamentos suficientes, devemos confirmar a inscrição.

                num += 1
                sub.status = Subscription.CONFIRMED_STATUS
                sub.save()

                processed_subs.append({
                    'sub': sub,
                    'to_pay': price_to_pay,
                    'paid': paid,
                })

            self.stdout.write(self.style.SUCCESS(
                'Inscrições pagas e pendentes: {}'.format(num)
            ))

            for item in processed_subs:
                self._print_subscription(item['sub'],
                                         item['to_pay'],
                                         item['paid'])

    def _print_subscription(self, subscription: Subscription, to_pay, paid):
        self.stdout.write(self.style.SUCCESS(
            " Atualizando inscrição PK: {}\n"
            "    Evento: {} ({})\n"
            "    Lote: {} ({})\n"
            "    Nome do Participante: {} (ID: {})\n"
            "    Horario de criação da inscrição: {}\n"
            "    Horario de modificação da inscrição: {}\n"
            "    Origem: {}\n"
            "    Completed: {}\n"
            "    Notificado: {}\n"
            "    E-mail do Participante: {}\n"
            "    A pagar: {}\n"
            "    Pago: {}\n".format(
                subscription.pk,
                subscription.event.name,
                subscription.lot.name,
                subscription.lot.pk,
                subscription.event.pk,
                subscription.person.name,
                subscription.person.pk,
                subscription.created,
                subscription.modified,
                subscription.get_origin_display(),
                subscription.completed,
                subscription.notified,
                subscription.person.email,
                to_pay,
                paid,
            )
        ))
