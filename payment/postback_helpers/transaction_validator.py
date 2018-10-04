from payment.helpers import TransactionLog
from payment.models import Transaction

"""
Objectives: 

    - Resgatar status da Transação encontrada;
    - Resgatar novo status da Transação enviado no Payload;
    - Validar se status da transação e novo status são diferentes;

"""


class TransactionValidator(object):

    def __init__(self,
                 payload: dict,
                 transaction_log: TransactionLog,
                 transaction: Transaction, ) -> None:
        self.payload = payload
        self.log = transaction_log
        self.transaction = transaction

        super().__init__()

    def fetch_current_status(self):
        """
            Resgatar status da Transação encontrada

        :return: str
        """
        status = self.transaction.status
        self.log.add_message('Status anterior: {}.'.format(status))
        return status

    def fetch_new_status(self):
        """
            Resgatar novo status da Transação enviado no Payload;

        :return: string
        """

        status = self.payload.get('current_status', '')

        self.log.add_message('Status a ser registrado: {}.'.format(
            status
        ))

        return status

    def validate(self):
        """

        :return: bool
        """

        existing_status = self.fetch_current_status()
        new_status = self.fetch_new_status()

        # Se não irá mudar o status de transação, não há o que processar.
        if existing_status == new_status:
            self.log.add_message(
                'Nada a ser feito: o status não mudou',
                save=True
            )

            return False

        return True

