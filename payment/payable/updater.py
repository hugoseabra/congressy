import logging
from datetime import datetime, timedelta
from decimal import Decimal
from pprint import pprint

import pagarme

from payment.exception import TransactionApiError
from payment.helpers import payment_helpers
from payment.models import SplitRule, Transaction, Payable
from payment.payable.credit_card import get_payables


def __notify_error(message, extra_data=None):
    logger = logging.getLogger(__name__)
    logger.error(message, extra=extra_data)


def update_payables(split_rule: SplitRule, check_hours_delay=8):
    """
    Atualiza recebíveis de uma transação

    :param split_rule: Model de Regra de rateamento do Pagar.me
    :param check_hours_delay: Delay de próxima checagem em horas
    """
    if split_rule.checkable is False:
        return

    now = datetime.now()
    next_check = now + timedelta(hours=check_hours_delay)

    transaction = Transaction.objects.get(pk=split_rule.transaction_id)

    event = transaction.subscription.event

    if event.finished is True:
        diff_days = event.date_end.date() - now.date()

        if diff_days.days > 3:
            # Terminou há mais de 3 dias
            split_rule.checkable = False
            split_rule.next_check = None
            split_rule.save()
            return

    is_boleto = transaction.type == Transaction.BOLETO
    is_cc = transaction.type == Transaction.CREDIT_CARD
    is_paid = transaction.paid

    if is_boleto is True and is_paid is False:
        # Boleto não pago não possuem recebíveis

        exp_date = transaction.boleto_expiration_date
        if exp_date and isinstance(exp_date, datetime):
            exp_date = exp_date.date()

        if exp_date and exp_date >= now.date():
            # boleto vencido.
            split_rule.checkable = False
            split_rule.next_check = None
            split_rule.save()
            return

        split_rule.next_check = next_check
        split_rule.save()
        return

    payable_qs = split_rule.payables

    if is_boleto is True and is_paid is True and payable_qs.count():
        # Boleto pago que já possui recebível já foi processado
        split_rule.checkable = False
        split_rule.next_check = None
        split_rule.save()
        return

    # NESTE PONTO EM DIANTE:
    # - Evento não inicado, em andamento ou finalizado em menos de 3 dias
    # - Transação ainda não sincronizada
    # - Regras de split com next_check hábil para o momento
    # - Cartão de crédito que já possui recebível previsto e poderá ser
    #   confirmado;
    # - Boleto pago que irá atualizar seus recebíveis;

    try:
        payables_trx = pagarme.transaction.payables(transaction.pagarme_id)

    except Exception as e:

        pprint(e)

        errors_msg = []
        if hasattr(e, 'args'):
            errors = [errs for errs in e.args]
            for error in errors[0]:
                if isinstance(error, dict):
                    errors_msg.append('{}: {}'.format(
                        error.get('parameter_name'),
                        error.get('message'),
                    ))
                else:
                    errors_msg.append(error)
        else:
            errors_msg.append(e)

        msg = 'Pagar.me: erro de transação: {}'.format(";".join(errors_msg))
        __notify_error(message=msg)
        raise TransactionApiError(
            'Algo deu errado com a comunicação com o provedor de pagamento.'
        )

    fee_percent = None

    if split_rule.charge_processing_fee is True:
        fee_percent = Decimal(2.99)

    simulator_payables = get_payables(
        recipient_id=split_rule.recipient_id,
        transaction_amount=transaction.amount,
        transaction_date=transaction.date_created.date(),
        payable_amount=split_rule.amount,
        installments=transaction.installments,
        fee_percent=fee_percent,
        antecipation_fee_percent=Decimal(1.99) if is_cc else None,
    )

    def get_simulator(recipient_id, installment):
        for sim in simulator_payables:
            if sim.recipient_id == recipient_id \
                    and sim.installment == installment:
                return sim

        return None

    for item in payables_trx:

        if item['recipient_id'] != split_rule.recipient_id:
            # Quem é você?
            continue

        simulator = get_simulator(
            item['recipient_id'],
            item.get('installment') or 1,
        )

        amount = payment_helpers.amount_as_decimal(str(item['amount']))

        if item['fee']:
            fee = payment_helpers.amount_as_decimal(str(item['fee']))
        else:
            fee = simulator.fee_amount

        if item['anticipation_fee']:
            antecipation_fee = payment_helpers.amount_as_decimal(
                str(item['anticipation_fee'])
            )
        else:
            # Taxa de antecipação somente para boleto
            antecipation_fee = simulator.get_antecipation_amount()

        if item['payment_date']:
            payment_date = datetime.strptime(
                item['payment_date'],
                "%Y-%m-%dT%H:%M:%S.%fZ"
            )
        else:
            payment_date = simulator.payment_date

        created = datetime.strptime(
            item['date_created'],
            "%Y-%m-%dT%H:%M:%S.%fZ"
        )

        try:
            payable = Payable.objects.get(
                split_rule=split_rule,
                pagarme_id=item['id'],
                type=item['type'],
                installment=item['installment'] or 1,
                recipient_id=item['recipient_id'],
                created=created,
            )
            payable.fee = fee
            payable.antecipation_fee = antecipation_fee
            payable.payment_date = payment_date
            payable.amount = amount
            payable.status = item['status']

            if item['status'] == Payable.STATUS_PAID:
                payable.synced = True

            payable.save()

        except Payable.DoesNotExist:
            Payable.objects.create(
                split_rule=split_rule,
                pagarme_id=item['id'],
                type=item['type'],
                status=item['status'],
                installment=item['installment'] or 1,
                recipient_id=item['recipient_id'],
                amount=amount,
                created=created,
                fee=fee,
                antecipation_fee=antecipation_fee,
                payment_date=payment_date,
                synced=item['status'] == Payable.STATUS_PAID,
            )

        if item['status'] == Payable.STATUS_PAID:
            split_rule.checkable = False
            split_rule.next_check = None
            split_rule.save()
