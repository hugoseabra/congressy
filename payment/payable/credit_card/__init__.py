"""
No Pagar.me Payable (saldo recebível) é um um item recebedor que é passível
de receber um pagamento, ter um pagamento disponível ou já ter recebido um
pagamento. Quantidade de itens é de acordo com o split da transação e
quantidade de parcelas (se transação parcelada).
"""

from datetime import date
from decimal import Decimal
from typing import List

from .payable import Payable
from .payable_date import CreditCardPayableDate
from .payable_part import get_part_amounts


def get_payables(recipient_id: str,
                 transaction_amount: Decimal,
                 transaction_date: date,
                 payable_amount: Decimal,
                 installments=1,
                 fee_percent: Decimal = None,
                 antecipation_fee_percent: Decimal = None) -> List[Payable]:
    """
    Resgata lista de recebíveis de acordo com os dados de uma transação.

    :param recipient_id: ID do recebedor
    :param transaction_amount: Valor total da transação
    :param transaction_date: Data da transação
    :param payable_amount: Valor do recebível (diferente da transação)
    :param installments: Número de parcelas da transação
    :param fee_percent: Taxa percentual a ser cobrada pela transação
    :param antecipation_fee_percent: Taxa percentual a ser cobrada pela
        antecipação
    :return: Lista de recebíveis
    """

    fee_part_amounts = list()

    if fee_percent:
        fee_amount = transaction_amount * (fee_percent / 100)
        fee_part_amounts = get_part_amounts(
            amount=fee_amount,
            installments=installments,
        )

    part_amounts = get_part_amounts(amount=payable_amount,
                                    installments=installments)

    payables = list()

    part = 1
    for part_amount in part_amounts:
        if fee_part_amounts:
            fee_amount = round(fee_part_amounts[part - 1], 2)
        else:
            fee_amount = 0

        payable = Payable(
            recipient_id=recipient_id,
            partial_amount=part_amount,
            transaction_date=transaction_date,
            fee_amount=fee_amount,
            installment=part,
            antecipation_fee_percent=antecipation_fee_percent,
        )
        payables.append(payable)
        part += 1

    return payables


__all__ = [
    'Payable',
    'CreditCardPayableDate',
    'get_part_amounts',
    'get_payables',
]
