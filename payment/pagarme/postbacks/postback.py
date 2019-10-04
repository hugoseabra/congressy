from decimal import Decimal

from payment.exception import (
    PostbackValueError,
    PostbackAmountDiscrepancyError,
)
from payment.helpers import TransactionDirector
from payment.models import Transaction
from payment.transaction_status_collection import TransactionStatusCollection


class Postback:
    """
    Responsabilidade: Estabelecer regras de transição de status de
    transação. Esta transição deve respeitar um status precedente, o tipo de
    transação para verificações de integridade e um montante para saber se a
    transição pode ser realizada.
    """

    def __init__(self,
                 transaction_pk: str,
                 transaction_status: str,
                 transaction_type: str,
                 transaction_amount: Decimal,
                 transaction_history: TransactionStatusCollection) -> None:

        self.transaction_pk = transaction_pk
        self.transaction_status = transaction_status
        self.transaction_amount = transaction_amount
        self.transaction_type = transaction_type
        self.transaction_history = transaction_history

        super().__init__()

    def get_new_status(self, payload: dict):

        # Validar se temos todos os dados necessários
        self._validate(payload)

        new_status = payload.get('current_status')

        # Se não irá mudar o status de transação, não há o que processar.
        if self.transaction_status == new_status:
            return self.transaction_status

        # Atualizando os status da Transaction
        status = TransactionDirector(
            status=new_status,
            old_status=self.transaction_status,
        ).direct()

        # Verifica se o status realmente mudou.
        if self.transaction_status == status:
            # Em caso de ser o mesmo status, vamos verificar se o ID de
            # transação no pagar.me é a mesma. Caso tenha mudado, significa que
            # houve um pedido de transação interna que o pagar.me reprocessou e
            # mudou o status que pode não ser conforme a máquina de estado
            # de status de transação.
            last_status = self.transaction_history.last()
            saved_payload_id = last_status['data']['id']
            payload_id = payload.get('id')

            if saved_payload_id != payload_id:
                # reseta regras de máquinas de status, ignorando a verificação.
                status = new_status

        return status

    def _validate(self, payload: dict):

        key = 'id'
        if not payload.get(key):
            msg = "No transaction ID in payload data"
            raise PostbackValueError(
                transaction_pk=self.transaction_pk,
                message=msg,
                payload=payload,
                missing_key_name=key,
            )

        # Garantindo que temos o novo status no payload
        key = 'current_status'
        try:
            new_status = payload.get(key)
            self._validate_status(new_status)
        except PostbackValueError as e:
            e.payload = payload
            e.missing_key_name = key
            raise e

        # Garantindo que temos o valor da compra no payload

        key = 'transaction[amount]'
        try:
            amount = payload.get(key)
            self._validate_amount(amount)
        except PostbackValueError as e:
            e.payload = payload
            e.missing_key_name = key
            raise e

        # Garantindo que temos link de boleto no payload
        if self.transaction_status == Transaction.WAITING_PAYMENT:
            try:
                boleto_url = payload.get('transaction[boleto_url]')
                self._validate_boleto_url(boleto_url)
            except PostbackValueError as e:
                e.payload = payload
                e.missing_key_name = 'transaction[boleto_url]'
                raise e

    # noinspection PyMethodMayBeStatic
    def _validate_status(self, new_status):
        if not new_status:
            msg = "No status for payload status: {}".format(new_status)
            raise PostbackValueError(
                message=msg,
                transaction_pk=self.transaction_pk,
            )

    def _validate_boleto_url(self, boleto_url):

        if self.transaction_type == Transaction.BOLETO \
                and self.transaction_status == Transaction.WAITING_PAYMENT:

            if not boleto_url:
                msg = "No value for payload boleto_url: {}".format(boleto_url)
                raise PostbackValueError(
                    message=msg,
                    transaction_pk=self.transaction_pk,
                )

    def _validate_amount(self, amount):
        if not amount:
            msg = "No value for payload amount: {}".format(amount)
            raise PostbackValueError(
                transaction_pk=self.transaction_pk,
                message=msg,
            )

        amount = Decimal(amount) / 100
        transaction_amount = round(self.transaction_amount, 2)

        # Se tivermos discrepância no valor vindo do pagarme, temos uma
        # possivel edição e irá causar problemas
        if transaction_amount != amount:
            msg = "Discrepancy in transaction.amount({}) " \
                  "and payload amount({})".format(transaction_amount,
                                                  amount)

            raise PostbackAmountDiscrepancyError(
                message=msg,
                transaction_pk=self.transaction_pk,
                existing_amount=self.transaction_amount,
                new_amount=amount,
            )
