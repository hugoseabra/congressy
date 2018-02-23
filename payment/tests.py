from django.test import TestCase
from statemachine.exceptions import TransitionNotAllowed

from gatheros_subscription.models import Subscription
from payment.exception import TransactionStatusIntegratorError
from payment.helpers import TransactionStateMachine, TransactionDirector, \
    TransactionSubscriptionStatusIntegrator
from payment.models import Transaction


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

    def test_regular_payment(self):
        self.assertEqual(self.tsm.current_state.value, 'processing')
        td = TransactionDirector(self.tsm.current_state.value, 'paid')
        self.assertEqual(td.direct(), 'paid')

    def test_regular_refused(self):
        self.assertEqual(self.tsm.current_state.value, 'processing')
        td = TransactionDirector(self.tsm.current_state.value, 'refused')
        self.assertEqual(td.direct(), 'refused')

    def test_delayed_payment(self):
        self.assertEqual(self.tsm.current_state.value, 'processing')
        self.tsm.awaiting_payment()
        self.assertEqual(self.tsm.current_state.value, 'waiting_payment')
        td = TransactionDirector(self.tsm.current_state.value, 'paid')
        self.assertEqual(td.direct(), 'paid')

    def test_delayed_refused(self):
        self.assertEqual(self.tsm.current_state.value, 'processing')
        self.tsm.awaiting_payment()
        self.assertEqual(self.tsm.current_state.value, 'waiting_payment')
        td = TransactionDirector(self.tsm.current_state.value, 'refused')
        self.assertEqual(td.direct(), 'refused')

    def test_refund(self):
        self.tsm = TransactionStateMachine(start_value='paid')
        self.assertEqual(self.tsm.current_state.value, 'paid')
        td = TransactionDirector(self.tsm.current_state.value, 'refunded')
        self.assertEqual(td.direct(), 'refunded')

    def test_delayed_refund(self):
        self.tsm = TransactionStateMachine(start_value='paid')
        self.assertEqual(self.tsm.current_state.value, 'paid')
        td = TransactionDirector(self.tsm.current_state.value,
                                 'pending_refund')
        self.assertEqual(td.direct(), 'pending_refund')
        self.tsm.paid_pending_refund()

    def test_pending_refund_to_refund(self):
        self.tsm = TransactionStateMachine(start_value='pending_refund')
        self.assertEqual(self.tsm.current_state.value, 'pending_refund')
        td = TransactionDirector(self.tsm.current_state.value,
                                 'refunded')
        self.assertEqual(td.direct(), 'refunded')
        self.tsm.refund_from_pending()
        self.assertEqual(self.tsm.current_state.value, 'refunded')


class TransactionSubscriptionStatusIntegratorTest(TestCase):

    def test_confirmed_status(self):

        states = ['paid']

        for state in states:
            tssi = TransactionSubscriptionStatusIntegrator(state)
            self.assertEqual(Subscription.CONFIRMED_STATUS, tssi.integrate())

    def test_cancelled_status(self):

        states = [
            'refused',
            'refunded',
        ]

        for state in states:
            tssi = TransactionSubscriptionStatusIntegrator(state)
            self.assertEqual(Subscription.CANCELED_STATUS, tssi.integrate())

    def test_waiting_status(self):

        states = [
            'processing',
            'waiting_payment',
            'chargeback'
            'pending_refund',
        ]

        for state in states:
            tssi = TransactionSubscriptionStatusIntegrator(state)
            self.assertEqual(Subscription.AWAITING_STATUS, tssi.integrate())

    def test_unknown_state(self):
        tssi = TransactionSubscriptionStatusIntegrator('unkown state')
        with self.assertRaises(TransactionStatusIntegratorError):
            tssi.integrate()
