from payment.helpers import TransactionStateMachine
from payment.exception import StateNotAllowedError


class TransactionDirector:

    def __init__(self, old_status, status):
        self.status = status
        self.old_status = old_status
        self.transaction_state_machine = TransactionStateMachine(
            start_value=old_status)

    def direct(self):

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

            if self.status == "chargeback":
                self.transaction_state_machine.chargeback()
            elif self.status == "pending_refund":
                self.transaction_state_machine.paid_pending_refund()
            elif self.status == "refunded":
                self.transaction_state_machine.pending_refund()
            else:
                raise StateNotAllowedError(
                    message='State not allowed for paid')

        elif self.old_status == "chargeback":

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
