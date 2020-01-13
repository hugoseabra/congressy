from datetime import datetime

from django.db.transaction import atomic

from payment.forms import PaymentForm
from payment.helpers import payment_helpers
from payment.models import Transaction, TransactionStatus
from payment.pagarme.forms import SubscriptionCheckoutForm
from payment.pagarme.postbacks.postback import Postback
from payment.transaction_status_collection import TransactionStatusCollection
from .exceptions import (
    PaymentNotCreatedError,
    TransactionSameStatusException,
)


def postback_processor(transaction_pk, transaction_data):
    transaction = Transaction.objects.get(uuid=transaction_pk)
    subscription = transaction.subscription
    event = subscription.event

    # status history
    history = TransactionStatusCollection()
    for status in transaction.statuses.all().order_by('pk'):
        history.add(
            created_on=status.date_created,
            status=status.status,
            data=status.data
        )

    post_back = Postback(
        transaction_pk=str(transaction.pk),
        transaction_amount=transaction.amount,
        transaction_status=transaction.status,
        transaction_type=transaction.type,
        transaction_history=history,
    )

    with atomic():
        # ================= TRANSACTION ====================================
        new_status = post_back.get_new_status(payload=transaction_data)

        if transaction.status == new_status:
            raise TransactionSameStatusException()

        # ================= TRANSACTION STATUS =============================

        # Registra status de transação.
        TransactionStatus.objects.create(
            transaction=transaction,
            data=transaction_data,
            date_created=datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            status=new_status,
        )

        # ==================================================================

        transaction.status = new_status

        # Alterando a URL de boleto
        if transaction.type == Transaction.BOLETO:
            boleto_url = transaction_data.get('transaction[boleto_url]')
            transaction.boleto_url = boleto_url

        transaction.save()

        # ============================ PAYMENT ================================
        if new_status == Transaction.PAID:

            # ===================== INSTALLMENT ===============================
            if transaction.part_id:
                part = transaction.part
                contract = part.contract

                # Paga parcela
                part.paid = True
                part.save()

                # Ao pagar a última parcela o contrato é encerrado.
                if contract.paid is False and contract.closed is False:
                    # Se contrato não foi encerrado...
                    # PRÓXIMA PARCELA
                    next_part = contract.parts.get(
                        paid=False,
                        installment_number=part.installment_number + 1
                    )

                    benefactor_id = None

                    if transaction.payer:
                        benefactor_id = transaction.payer.benefactor_id

                    checkout_form = SubscriptionCheckoutForm(data={
                        'event_pk': event.pk,
                        'subscription_pk': contract.subscription_id,
                        'benefactor_pk': benefactor_id,
                        'transaction_type': Transaction.BOLETO,
                        'num_installments': contract.num_installments,
                        'installment_part': next_part.pk,
                        'interests_amount': payment_helpers.as_payment_amount(
                            next_part.interests_amount,
                        )
                    })

                    if checkout_form.is_valid() is False:
                        raise Exception(checkout_form.errors)

                    checkout_form.save()

        elif new_status == Transaction.REFUNDED:

            # ===================== INSTALLMENT ===============================
            if transaction.part_id:
                # Isso irá reabrir o contrato de parcelamento.
                transaction.part.paid = False
                transaction.part.save()

    return transaction
