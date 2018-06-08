"""
    Main implantation of a director responsible for changing the Transaction
    State Machine Status
"""
from payment.helpers import TransactionStateMachine
from payment.exception import StateNotAllowedError


class TransactionDirector:
    """
        Class implementation of the Transaction State Machine Director
    """

    def __init__(self, old_status, status):
        """

        :param old_status (string): the old status of the machine, used as the
                                    initial starting value for the directors
                                    instance of the Transaction State Machine.
                                    Typically retrieved from a database.
        :param status (string): the new desired state for the State Machine.
                                Typically is received from a third-party like
                                Pagar.me
        """
        self.status = status
        self.old_status = old_status
        self.transaction_state_machine = TransactionStateMachine(
            start_value=old_status)

    def direct(self):
        """

        :return: status (string): the current state of the transaction machine
                                  after applying the desired change of state

        :raises:

            StateNotAllowedError: when attempts to apply an unallowed
                                  business rule change of state

            TransitionNotAllowed: when attempts to apply an unallowed state
                                  machine change of state

        """

        if self.old_status == "processing":

            if self.status == 'waiting_payment':
                self.transaction_state_machine.awaiting_payment()
            elif self.status == "refused":
                self.transaction_state_machine.refuse()
            elif self.status == "paid":
                self.transaction_state_machine.pay()
            else:
                raise StateNotAllowedError(
                    message='State not allowed for processing')

        elif self.old_status == "waiting_payment":

            if self.status == "paid":
                self.transaction_state_machine.awaiting_pay()
            elif self.status == "refused":
                self.transaction_state_machine.awaiting_refused()
            else:
                raise StateNotAllowedError(
                    message='State not allowed for waiting_payment')

        elif self.old_status == "paid":

            if self.status == "chargedback":
                self.transaction_state_machine.chargeback()
            elif self.status == "pending_refund":
                self.transaction_state_machine.paid_pending_refund()
            elif self.status == "refunded":
                self.transaction_state_machine.paid_refund()
            else:
                raise StateNotAllowedError(
                    message='State not allowed for paid')

        elif self.old_status == "chargedback":

            if self.status == "paid":
                self.transaction_state_machine.paid_chargeback()
            elif self.status == "refunded":
                self.transaction_state_machine.refund_chargeback()
            elif self.status == "pending_refund":
                self.transaction_state_machine.delayed_refund()
            else:
                raise StateNotAllowedError(
                    message='State not allowed for chargeback')

        elif self.old_status == "pending_refund":
            if self.status == 'refunded':
                self.transaction_state_machine.refund_from_pending()
            else:
                raise StateNotAllowedError(
                    message='State not allowed for pending_refund')

        elif self.old_status == "refunded" or self.old_status == "refused":
            pass

        return self.transaction_state_machine.current_state.value
