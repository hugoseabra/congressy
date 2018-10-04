from core.helpers import sentry_log
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
        Responsabilidade: processar atualização de transação

        Processar atualização constitui em realizar as seguinte ações:

            -  validar dados de entrada
            - alterar os seguintes atributos de Transaction
                - status;
                - vencimento de boleto;
                - url de boleto
                - url do boleto no campo de data(json)
    """

    def __init__(self, transaction: Transaction) -> None:
        self.transaction = transaction
        super().__init__()

    def _validate_new_data(self, payload: dict):

        # Garantindo que temos o novo status no payload
        new_status = payload.get('current_status')
        if not new_status:
            msg = "No status for payload status: {}".format(new_status)
            raise PostbackValueError(msg)

        # Se não irá mudar o status de transação, não há o que processar.
        if self.transaction.status == new_status:
            msg = "transaction.status({}) is equal to payload status({})" \
                .format(self.transaction.status, new_status)
            raise PostbackSameStatusError(msg)

        # Garantindo que temos o valor da compra no payload
        amount = payload.get('amount')
        if not amount:
            msg = "No value for payload amount: {}".format(amount)
            raise PostbackValueError(msg)

        # Se tivermos discrepância no valor vindo do pagarme, temos uma
        # possivel edição e irá causar problemas
        if self.transaction.amount != amount:
            msg = "Discrepancy in transaction.amount({}) " \
                  "and payload amount({})".format(self.transaction.amount,
                                                  amount)

            sentry_log(
                message=msg,
                type='error',
                extra_data={
                    'transaction': self.transaction.pk,
                    'transaction_status': self.transaction.status,
                    'incoming_status': new_status,
                    'send_data': payload,
                },
                notify_admins=True,
            )

            raise PostbackAmountDiscrepancyError(msg)

        # Garantindo que temos link de boleto no payload
        if self.transaction.type == Transaction.BOLETO:
            boleto_url = payload.get('transaction[boleto_url]')
            if not boleto_url:
                msg = "No value for payload boleto_url: {}".format(boleto_url)
                raise PostbackValueError(msg)

    def update_transaction(self, payload: dict):
        self._validate_new_data(payload)

        # Atualizando os status da Transaction
        status = TransactionDirector(
            status=payload.get('current_status'),
            old_status=self.transaction.status,
        ).direct()

        self.transaction.status = status

        # Alterando a URL de boleto
        if self.transaction.type == Transaction.BOLETO:
            boleto_url = payload.get('transaction[boleto_url]')
            self.transaction.data['boleto_url'] = boleto_url
            self.transaction.boleto_url = boleto_url

        self.transaction.save()

        return self.transaction
