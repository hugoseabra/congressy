"""
    Main implementation of a class for integrating/translating transaction
    states to subscription status

    See: doc/Diagramas/StateMachine/CONGRESSY_GDS-LPS-Transacao_v01.jpg

"""
from gatheros_subscription.models import Subscription
from payment.exception import TransactionStatusIntegratorError


class TransactionSubscriptionStatusIntegrator:
    """
        Class responsible for integrating Transaction states to
            Subscription statuses

        Attributes:

            awaiting_status (list): list of strings representing allowed
                                    transaction states to become subscription
                                    awaiting status.

            confirmed_status (list): list of strings representing allowed
                                    transaction states to become subscription
                                    confirmed status.

            cancelled_status (list): list of strings representing allowed
                                    transaction states to become subscription
                                    cancelled status.
    """

    awaiting_status = [
        'processing',
        'waiting_payment',
        'pending_refund',
        'refused',
        'refunded',
    ]

    confirmed_status = [
        'paid',
        'chargeback',
    ]

    cancelled_status = []

    def __init__(self, transaction_state):
        """
            Class constructor

        :param transaction_state (string): String representing the
            transaction state.
        """
        self.transaction_state = transaction_state

    def integrate(self):
        """
        Method responsible for applying the integration/translation of
            Transaction states to Subscription status

        :return:
            Subscription.status (string)

        :raises:
            TransactionStatusIntegratorError: If self.transaction_state is not
                                              in any of the lists.
                                              Unknown state.
        """
        if self.transaction_state in self.awaiting_status:
            return Subscription.AWAITING_STATUS
        elif self.transaction_state in self.confirmed_status:
            return Subscription.CONFIRMED_STATUS
        elif self.transaction_state in self.cancelled_status:
            return Subscription.CANCELED_STATUS
        else:

            msg = 'Unknown status for {}'.format(self.transaction_state)

            raise TransactionStatusIntegratorError(msg)
