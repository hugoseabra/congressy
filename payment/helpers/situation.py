"""
Helper para retornar situação da transação:
1. a partir de um lote, todas as inscrições;
2. a partir de uma inscrição;

Objeto de situação esperado:
    - type: boleto ou credit_card;
    - type_description: boleto ou credit_card;
    - amount: valor da inscrição;
    - status: status da transação;
    - status_description: display do status da transação;
    - issue_date:
        - se boleto, data do vencimento;
        - se cartão, data da transação;
"""
from datetime import datetime
from django.db.models import ObjectDoesNotExist

from payment.exception import TransactionNotFound


def get_subscriptions_situations(lot):
    """ Resgata situações das inscrições de um lote. """
    situations = {}
    for sub in lot.subscriptions.all():
        situations[sub.pk] = get_situations(sub)

    return situations


def get_situations(subscription):
    """ Resgata uma lista de situações de transações de uma inscrição. """
    lot = subscription.lot

    if lot.price is None or (lot.price is not None and int(lot.price) == 0):
        raise TransactionNotFound()

    try:
        situations = []
        for transaction in subscription.transactions.all():
            data = transaction.data
            issue_date = ''

            if transaction.type == transaction.BOLETO:
                exp_date = data.get('boleto_expiration_date')
                if exp_date:
                    issue_date = datetime.strptime(
                        exp_date,
                        "%Y-%m-%dT%H:%M:%S.%fZ"
                    )

            situations.append({
                'type': transaction.type,
                'type_description': transaction.get_type_display(),
                'amount': transaction.amount,
                'status': transaction.status,
                'status_description': transaction.get_status_display(),
                'issue_date': issue_date,
            })

        return situations

    except (AttributeError, ObjectDoesNotExist):
        raise TransactionNotFound()
