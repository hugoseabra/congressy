from decimal import Decimal

from django.core.management.base import BaseCommand

from gatheros_event.models import Event
from gatheros_subscription.models import Subscription
from installment.models import Contract
from payment.models import Transaction


class Command(BaseCommand):
    help = 'Mostra informações gerais sobre valores de pagamento de um evento.'

    def add_arguments(self, parser):
        parser.add_argument('event_id', type=int)

    def handle(self, *args, **options):

        event_id = options.get('event_id')

        try:
            event = Event.objects.get(pk=event_id)

        except Event.DoesNotExist:
            self.stderr.write(
                'Evento com ID "{}" não encontrado.'.format(event_id)
            )
            return

        self.stdout.write(self.style.SUCCESS(
            'Evento: {}'.format(event.name)
        ))
        self.stdout.write(self.style.SUCCESS(
            'Org: {}'.format(event.organization.name)
        ))
        print()

        self._show_subscription_reports(event)
        self._show_internal_subscription_reports(event)
        self._show_paid_amounts(event)
        self._show_pending_amounts(event)
        self._show_cc_reports(event)
        self._show_boleto_reports(event)
        self._show_installments_reports(event)

    def _show_subscription_reports(self, event):

        subs = Subscription.objects.filter(
            event_id=event.pk,
            completed=True,
            test_subscription=False,
            origin=Subscription.DEVICE_ORIGIN_HOTSITE,
        )

        free = 0
        free_pending = 0
        paid = 0
        paid_pending = 0
        total_paid = 0
        total_free = 0
        total = subs.count()

        for sub in subs:
            if sub.free:
                if sub.status == Subscription.CONFIRMED_STATUS:
                    free += 1
                else:
                    free_pending += 1

                total_free += 1
            else:
                if sub.status == Subscription.CONFIRMED_STATUS:
                    paid += 1
                else:
                    paid_pending += 1

                total_paid += 1

        print()
        title = 'SOBRE INSCRIÇÕES HOTSITE'
        print(title)
        print('=' * len(title))

        print('- Confirmadas (Gratuitas x Pagas): ', end='')
        self.stdout.write(self.style.SUCCESS(
            '{} x {}'.format(free, paid)
        ))

        print('-   Pendentes (Gratuitas x Pagas): ', end='')
        self.stdout.write(self.style.SUCCESS(
            '{} x {}'.format(free_pending, paid_pending)
        ))

        print('-      Totais (Gratuitas x Pagas): ', end='')
        self.stdout.write(self.style.SUCCESS(
            '{} x {}'.format(total_free, total_paid)
        ))

        print('-                           Total: ', end='')
        self.stdout.write(self.style.SUCCESS('{}'.format(total)))

    def _show_internal_subscription_reports(self, event):

        subs = Subscription.objects.filter(
            event_id=event.pk,
            completed=True,
            test_subscription=False,
            origin__in=[
                Subscription.DEVICE_ORIGIN_MANAGE,
                Subscription.DEVICE_ORIGIN_CSV_IMPORT,
            ]
        )

        free = 0
        free_pending = 0
        paid = 0
        paid_pending = 0

        for sub in subs:
            if sub.free:
                if sub.status == Subscription.CONFIRMED_STATUS:
                    free += 1
                else:
                    free_pending += 1
            else:
                if sub.status == Subscription.CONFIRMED_STATUS:
                    paid += 1
                else:
                    paid_pending += 1

        transactions = Transaction.objects.filter(
            manual=True,
            subscription__event_id=event.pk,
            subscription__completed=True,
            subscription__test_subscription=False,
            subscription__origin=Subscription.DEVICE_ORIGIN_MANAGE,
            subscription__status=Subscription.CONFIRMED_STATUS,
        )

        manual_with_contract = list()
        manual_no_contract = list()
        manual = list()

        for trans in transactions:
            if trans.part_id:
                manual_with_contract.append(trans.liquid_amount)
            else:
                manual_no_contract.append(trans.liquid_amount)

            manual.append(trans.liquid_amount)

        print()
        title = 'SOBRE INSCRIÇÕES INTERNAS'
        print(title)
        print('=' * len(title))

        print('- Confirmadas (Gratuitas x Pagas): ', end='')
        self.stdout.write(self.style.SUCCESS(
            '{} x {}'.format(free, paid)
        ))

        print('-   Pendentes (Gratuitas x Pagas): ', end='')
        self.stdout.write(self.style.SUCCESS(
            '{} x {}'.format(free_pending, paid_pending)
        ))

        print('-      Totais (Gratuitas x Pagas): ', end='')
        self.stdout.write(self.style.SUCCESS(
            '{} x {}'.format(free + free_pending, paid + paid_pending)
        ))

        print('-        Pag. Manuais s/ Contrato: ', end='')
        self.stdout.write(self.style.SUCCESS(
            'R$ {} ({})'.format(
                sum(manual_with_contract),
                len(manual_with_contract),
            )
        ))

        print('-        Pag. Manuais c/ Contrato: ', end='')
        self.stdout.write(self.style.SUCCESS(
            'R$ {} ({})'.format(
                sum(manual_no_contract),
                len(manual_no_contract),
            )
        ))

        print('-            Pag. Manuais - geral: ', end='')
        self.stdout.write(self.style.SUCCESS(
            'R$ {} ({})'.format(
                sum(manual),
                len(manual),
            )
        ))

    def _show_paid_amounts(self, event):

        paid_boletos = list()
        paid_cc = list()
        paid_manual = list()
        paid_part = list()
        total_paid_pagarme = list()
        total_paid_manual = list()
        total_paid = list()

        transactions = Transaction.objects.filter(
            subscription__event_id=event.pk,
            status=Transaction.PAID,
        )

        for trans in transactions:

            total_paid.append(trans.liquid_amount)

            if trans.manual:
                total_paid_manual.append(trans.liquid_amount)

                if trans.part_id:
                    paid_part.append(trans.liquid_amount)
                else:
                    paid_manual.append(trans.liquid_amount)

                continue

            total_paid_pagarme.append(trans.liquid_amount)

            if trans.type == Transaction.BOLETO:
                paid_boletos.append(trans.liquid_amount)
                continue

            if trans.type == Transaction.CREDIT_CARD:
                paid_cc.append(trans.liquid_amount)

        print()
        title = 'PAGAMENTO DE INSCRIÇÕES'
        print(title)
        print('=' * 45)

        print('-              CC: ', end='')
        self.stdout.write(self.style.SUCCESS(
            'R$ {} ({})'.format(sum(paid_cc), len(paid_cc))
        ))

        print('-          Boleto: ', end='')
        self.stdout.write(self.style.SUCCESS(
            'R$ {} ({})'.format(sum(paid_boletos), len(paid_boletos))
        ))

        print('- Manual s/ Parc.: ', end='')
        self.stdout.write(self.style.SUCCESS(
            'R$ {} ({})'.format(sum(paid_manual), len(paid_manual))
        ))

        print('- Manual c/ Parc.: ', end='')
        self.stdout.write(self.style.SUCCESS(
            'R$ {} ({})'.format(sum(paid_part), len(paid_part))
        ))

        print('- ------------------')

        print('- Total Pagamentos (provedor): ', end='')
        self.stdout.write(self.style.SUCCESS(
            'R$ {} ({})'.format(
                sum(total_paid_pagarme),
                len(total_paid_pagarme),
            )
        ))

        print('-   Total Pagamentos (manual): ', end='')
        self.stdout.write(self.style.SUCCESS(
            'R$ {} ({})'.format(sum(total_paid_manual), len(total_paid_manual))
        ))

        print('- ------------------')

        print('- Total Pagamentos (geral): ', end='')
        self.stdout.write(self.style.SUCCESS(
            'R$ {} ({})'.format(sum(total_paid), len(total_paid))
        ))

    def _show_pending_amounts(self, event):

        pending_part = list()
        pending_subs = list()
        total_pending = list()

        subs_qs = Subscription.objects.filter(
            event_id=event.pk,
            status=Subscription.AWAITING_STATUS,
            completed=True,
            test_subscription=False,
            lot__price__gt=0,
        )

        for sub in subs_qs:
            price = sub.lot.get_liquid_price()

            total_pending.append(price)

            contracts_qs = sub.installment_contracts.filter(
                status=Contract.OPEN_STATUS,
            )

            if contracts_qs.count() == 0:
                pending_subs.append(price)

            else:
                pending_part.append(price)

        print()
        title = 'PENDÊNCIAS DE INSCRIÇÕES'
        print(title)
        print('=' * 45)

        print('-  Sem parcelamento: ', end='')
        self.stdout.write(self.style.SUCCESS(
            'R$ {} ({})'.format(sum(pending_subs), len(pending_subs))
        ))

        print('-  Com parcelamento: ', end='')
        self.stdout.write(self.style.SUCCESS(
            'R$ {} ({})'.format(sum(pending_part), len(pending_part))
        ))

        print('- ------------------')

        print('- Pendência Total (geral): ', end='')
        self.stdout.write(self.style.SUCCESS(
            'R$ {} ({})'.format(sum(total_pending), len(total_pending))
        ))

    def _show_cc_reports(self, event):

        transactions = Transaction.objects.filter(
            type=Transaction.CREDIT_CARD,
            manual=False,
            subscription__event_id=event.pk,
            subscription__completed=True,
            subscription__test_subscription=False,
        ).exclude(
            status=Transaction.WAITING_PAYMENT,
        )

        paid = list()
        refused = list()
        refunded = list()
        chargedback = list()

        total = Decimal(0)

        for trans in transactions:
            if trans.status == Transaction.PAID:
                paid.append(trans.liquid_amount)
                total += trans.liquid_amount
            elif trans.status == Transaction.REFUSED:
                refused.append(trans.liquid_amount)
                total += trans.liquid_amount
            elif trans.status == Transaction.REFUNDED:
                refunded.append(trans.liquid_amount)
                total += trans.liquid_amount
            elif trans.status == Transaction.CHARGEDBACK:
                chargedback.append(trans.liquid_amount)
                total += trans.liquid_amount

        paid_perc = round((sum(paid) * 100) / total, 2)
        refused_perc = round((sum(refused) * 100) / total, 2)
        refunded_perc = round((sum(refunded) * 100) / total, 2)
        chargedback_perc = round((sum(chargedback) * 100) / total, 2)

        print()
        title = 'SOBRE CARTÕES DE CRÉDITO'
        print(title)
        print('=' * 45)

        print('- Pagos: ', end='')
        self.stdout.write(self.style.SUCCESS(
            'R$ {} ({}) - {}%'.format(sum(paid), len(paid), paid_perc)
        ))

        print('- Recusados: ', end='')
        self.stdout.write(self.style.SUCCESS(
            'R$ {} ({}) - {}%'.format(
                sum(refused),
                len(refused),
                refused_perc,
            )
        ))

        print('- Estornados: ', end='')
        self.stdout.write(self.style.SUCCESS(
            'R$ {} ({}) - {}%'.format(
                sum(refunded),
                len(refunded),
                refunded_perc,
            )
        ))

        print('- Chargedbacks: ', end='')
        self.stdout.write(self.style.SUCCESS(
            'R$ {} ({}) - {}%'.format(
                sum(chargedback),
                len(chargedback),
                chargedback_perc,
            )
        ))

    def _show_boleto_reports(self, event):

        print()
        title = 'SOBRE BOLETOS'
        print(title)
        print('=' * 45)

        transactions = Transaction.objects.filter(
            subscription__event_id=event.pk,
            subscription__completed=True,
            subscription__test_subscription=False,
            type=Transaction.BOLETO,
            manual=False,
        ).exclude(
            status=Transaction.WAITING_PAYMENT,
        )

        paid = list()
        refused = list()
        refunded = list()

        total = Decimal(0)

        for trans in transactions:
            if trans.status == Transaction.PAID:
                paid.append(trans.liquid_amount)
                total += trans.liquid_amount
            elif trans.status == Transaction.REFUSED:
                refused.append(trans.liquid_amount)
                total += trans.liquid_amount
            elif trans.status == Transaction.REFUNDED:
                refunded.append(trans.liquid_amount)
                total += trans.liquid_amount

        paid_perc = round((sum(paid) * 100) / total, 2)
        refused_perc = round((sum(refused) * 100) / total, 2)
        refunded_perc = round((sum(refunded) * 100) / total, 2)

        print('-      Pagos: ', end='')
        self.stdout.write(self.style.SUCCESS(
            'R$ {} ({}) - {}%'.format(sum(paid), len(paid), paid_perc)
        ))

        print('-  Recusados: ', end='')
        self.stdout.write(self.style.SUCCESS(
            'R$ {} ({}) - {}%'.format(
                sum(refused),
                len(refused),
                refused_perc,
            )
        ))

        print('- Estornados: ', end='')
        self.stdout.write(self.style.SUCCESS(
            'R$ {} ({}) - {}%'.format(
                sum(refunded),
                len(refunded),
                refunded_perc,
            )
        ))

    def _show_installments_reports(self, event):

        cancelled = 0
        pending = 0
        paid = 0
        total = list()

        contracts = Contract.objects.filter(
            subscription__event_id=event.pk
        )

        for c in contracts:
            total.append(c.amount)

            if c.status == Contract.OPEN_STATUS:
                pending += 1
            elif c.status == Contract.CANCELLED_STATUS:
                cancelled += 1
            elif c.status == Contract.FULLY_PAID_STATUS:
                paid += 1

        print()
        title = 'CONTRATOS DE PARCELAMENTO'
        print(title)
        print('=' * len(title))

        print('- Contratos Cancelados: ', end='')
        self.stdout.write(self.style.SUCCESS(
            '{}'.format(cancelled)
        ))

        print('-  Contratos Pendentes: ', end='')
        self.stdout.write(self.style.SUCCESS(
            '{}'.format(pending)
        ))

        print('-      Contratos Pagos: ', end='')
        self.stdout.write(self.style.SUCCESS(
            '{}'.format(paid)
        ))

        print('-   Total em Contratos: ', end='')
        self.stdout.write(self.style.SUCCESS(
            'R$ {} ({})'.format(sum(total), len(total))
        ))
