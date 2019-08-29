from datetime import datetime

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.db.transaction import atomic

from payment.models import SplitRule, Transaction
from payment.payable.updater import update_payables


class Command(BaseCommand):
    help = 'Atualizando todos os recebíveis pendentes de verificação.'

    def handle(self, *args, **options):
        now = datetime.now()

        # Verifica todas as regras que estejam com recebíveis agendadas para
        # verificação, excluindo as regras que não possuem recebíveis agendados
        split_rule_qs = SplitRule.objects.filter(
            Q(next_check__isnull=True) | Q(next_check__lte=now),
            checkable=True,
        ).order_by('created')[:500]

        num_boletos = len([
            sr.uuid
            for sr in split_rule_qs
            if sr.transaction.type == Transaction.BOLETO
        ])

        self.stdout.write('# Boletos: {}'.format(
            self.style.SUCCESS(num_boletos or '0')
        ))

        num_cc = len([
            sr.uuid
            for sr in split_rule_qs
            if sr.transaction.type == Transaction.CREDIT_CARD
        ])
        self.stdout.write('# Cartões de Crédito: {}'.format(
            self.style.SUCCESS(num_cc or '0')
        ))

        with atomic():
            for split_rule in split_rule_qs:
                update_payables(split_rule)
