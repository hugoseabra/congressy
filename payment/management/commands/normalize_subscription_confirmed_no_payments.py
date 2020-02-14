from datetime import datetime

from django.core.management.base import BaseCommand
from django.db.models import Count, Sum
from django.db.transaction import atomic

from gatheros_subscription.models import Subscription
from payment.models import Transaction


class Command(BaseCommand):
    help = 'Atualiza inscrições com confirmadas, com lote pagos mas sem' \
           ' pagamento nenhum.'

    def handle(self, *args, **options):

        subs = Subscription.objects.annotate(
            num_trans=Count('transactions')
        ).filter(
            status='confirmed',
            lot__price__gt=0,
            num_trans=0
        )

        with atomic():
            num = 0
            processed_subs = list()

            for sub in subs:
                price_to_pay = sub.lot.get_calculated_price()

                processed_subs.append({
                    'sub': sub,
                    'to_pay': price_to_pay,
                    'status': sub.status,
                })

                num += 1
                sub.status = Subscription.AWAITING_STATUS
                sub.save()


            msg1 = 'Inscrições confirmadas, com lote pago e sem' \
                   ' pagamento: {}'.format(num)
            self.stdout.write(self.style.SUCCESS(msg1))

            for item in processed_subs:
                self._print_subscription(item['sub'],
                                         item['to_pay'])

    def _print_subscription(self, subscription: Subscription, to_pay, status):
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
            "    Status: {}\n"
            "    A pagar: {}\n".format(
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
                status,
                to_pay,
            )
        ))
