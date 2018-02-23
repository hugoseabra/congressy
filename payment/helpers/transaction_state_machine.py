# -*- coding: utf-8 -*-
""" Transaction State Machine implementation."""

from statemachine import StateMachine, State


class TransactionStateMachine(StateMachine):
    """
        Class responsible for implementing the State Machine.

        Attributes:
            processing (State): Default initial starting state. Represents the
                                 processing state.
            paid (State): Represents the paid state.
            waiting_payment (State): Represents the waiting for payment state.
            pending_refund (State): Represents the waiting for refund  state.
            refused (State): Represents the refused state.
            chargeback (State): Represents the chargedback state.
        Todo:
            * Finish documenting the attributes/functions.
    """

    processing = State('processing', initial=True)
    paid = State('paid')
    refunded = State('refunded')
    waiting_payment = State('waiting_payment')
    pending_refund = State('pending_refund')
    refused = State('refused')
    chargeback = State('chargeback')

    # Process
    awaiting_payment = processing.to(waiting_payment)
    refuse = processing.to(refused)
    pay = processing.to(paid)

    # Waiting for payments
    awaiting_pay = waiting_payment.to(paid)
    awaiting_refused = waiting_payment.to(refused)

    # Chargeback
    paid_chargeback = chargeback.to(paid)
    refund_chargeback = chargeback.to(refunded)
    delayed_refund = chargeback.to(pending_refund)

    # Paid
    chargedback = paid.to(chargeback)
    paid_refund = paid.to(refunded)
    paid_pending_refund = paid.to(pending_refund)

    # Pending Refused
    refund_from_pending = pending_refund.to(refunded)
