import logging
from datetime import datetime
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


def update_payables(split_rule: SplitRule):
    """
    Atualiza recebíveis de uma transação

    :param split_rule: Model de Regra de rateamento do Pagar.me
    """
    transaction = split_rule.transaction

    is_boleto = transaction.type == Transaction.BOLETO
    is_cc = transaction.type == Transaction.CREDIT_CARD
    paid = transaction.paid

    if is_boleto is True and paid is False:
        # Boleto não pago não possuem recebíveis
        return

    payable_qs = split_rule.payables

    if is_boleto is True and paid is True and payable_qs.count():
        # Boleto pago que já possui recebível já foi processado
        return

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
                status=item['status'],
                installment=item['installment'] or 1,
                recipient_id=item['recipient_id'],
                created=created,
            )
            payable.fee = fee
            payable.antecipation_fee = antecipation_fee
            payable.payment_date = payment_date
            payable.amount = amount

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
            )
