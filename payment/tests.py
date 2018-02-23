from django.test import TestCase
from payment.helpers import TransactionStateMachine
from payment.models import Transaction
from statemachine.exceptions import TransitionNotAllowed


class TransactionStateMachineTest(TestCase):

    def setUp(self):
        self.tsm = TransactionStateMachine()

    def test_default_starting_value(self):
        self.assertEqual(self.tsm.current_state.value, Transaction.PROCESSING)

    def test_skipping_a_state(self):
        with self.assertRaises(TransitionNotAllowed):
            self.tsm.refund_from_pending()

    def test_moving_state(self):
        self.tsm.awaiting_payment()
        self.assertEqual(self.tsm.current_state.value,
                         Transaction.WAITING_PAYMENT)


class TransactionDirectorTest(TestCase):


    def setUp(self):
        self.transaction = Transaction.objects.first()
        self.tsm = TransactionStateMachine()
        self.possible_status = [s.identifier for s in self.tsm.states]

    def test_fail(self):
        self.fail('adasda')
