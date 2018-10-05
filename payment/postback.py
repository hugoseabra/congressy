from decimal import Decimal

from payment.helpers import TransactionDirector
from .models import Transaction


class PostbackSameStatusError(Exception):
    pass


class PostbackAmountDiscrepancyError(Exception):
    pass


class PostbackValueError(Exception):
    pass


class Postback(object):
    """
        Responsabilidade: Estabelecer regras de transição de status de
        transação. Esta transição deve respeitar um status precedente, o tipo
        de transação para verificações de integridade e um montante para
        saber se a transição pode ser realizada.
    """

    def __init__(self,
                 transaction_status: str,
                 transaction_type: str,
                 transaction_amount: Decimal) -> None:

        self.transaction_status = transaction_status
        self.transaction_amount = transaction_amount
        self.transaction_type = transaction_type

        super().__init__()

    def get_new_status(self, payload: dict):

        # Validar se temos todos os dados necessários
        self._validate(payload)

        new_status = payload.get('current_status')
        # Se não irá mudar o status de transação, não há o que processar.
        if self.transaction_status != new_status:
            return self.transaction_status

        # Atualizando os status da Transaction
        status = TransactionDirector(
            status=new_status,
            old_status=self.transaction_status,
        ).direct()

        return status

    def _validate(self, payload: dict):

        # Garantindo que temos o novo status no payload
        new_status = payload.get('current_status')
        self._validate_status(new_status)

        # Garantindo que temos o valor da compra no payload
        amount = payload.get('amount')
        self._validate_amount(amount)

        # Garantindo que temos link de boleto no payload
        boleto_url = payload.get('transaction[boleto_url]')
        self._validate_boleto_url(boleto_url)

    # noinspection PyMethodMayBeStatic
    def _validate_status(self, new_status):
        if not new_status:
            msg = "No status for payload status: {}".format(new_status)
            raise PostbackValueError(msg)

    def _validate_amount(self, amount):
        if not amount:
            msg = "No value for payload amount: {}".format(amount)
            raise PostbackValueError(msg)

        # Se tivermos discrepância no valor vindo do pagarme, temos uma
        # possivel edição e irá causar problemas
        if self.transaction_amount != amount:
            msg = "Discrepancy in transaction.amount({}) " \
                  "and payload amount({})".format(self.transaction_amount,
                                                  amount)

            raise PostbackAmountDiscrepancyError(msg)

    def _validate_boleto_url(self, boleto_url):

        if self.transaction_type == Transaction.BOLETO:

            if not boleto_url:
                msg = "No value for payload boleto_url: {}".format(boleto_url)
                raise PostbackValueError(msg)
