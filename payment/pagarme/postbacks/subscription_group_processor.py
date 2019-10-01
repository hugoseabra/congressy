from datetime import datetime

from django.db.transaction import atomic

from payment.forms import GroupPaymentForm
from payment.helpers import payment_helpers
from payment.models import GroupTransaction, GroupTransactionStatus
from payment.pagarme.forms import SubscriptionGroupCheckoutForm
from payment.pagarme.postbacks.postback import Postback
from payment.transaction_status_collection import TransactionStatusCollection
from .exceptions import (
    PaymentNotCreatedError,
    TransactionSameStatusException,
)


def postback_processor(transaction_pk, transaction_data):
    transaction = GroupTransaction.objects.get(uuid=transaction_pk)
    event = transaction.subscription_group.event

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
        GroupTransactionStatus.objects.create(
            group_transaction=transaction,
            data=transaction_data,
            date_created=datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            status=transaction_data.get('current_status'),
        )

        # ==================================================================

        transaction.status = new_status

        # Alterando a URL de boleto
        if transaction.type == GroupTransaction.BOLETO:
            boleto_url = transaction_data.get('transaction[boleto_url]')
            transaction.boleto_url = boleto_url

        transaction.save()

        # ============================ PAYMENT ================================
        if new_status == GroupTransaction.PAID:

            payment_form = GroupPaymentForm(
                subscription_group=transaction.subscription_group,
                group_leader=transaction.group_leader,
                group_transaction=transaction,
                data={
                    'cash_type': transaction.type,
                    'amount': transaction.amount,
                    'discount_amount': transaction.discount_amount,
                    'installment_interests_amount':
                        transaction.installment_interests_amount,
                    'liquid_amount': transaction.liquid_amount,
                },
            )

            for sub in transaction.subscriptions.all():
                payment_form.add_subscription_pk(sub.pk)

            if not payment_form.is_valid():
                error_msgs = []
                for field, errs in payment_form.errors.items():
                    error_msgs.append(str(errs))

                msg = 'Erro ao criar pagamento de uma transação: ' \
                      ' {}'.format("".join(error_msgs))

                raise PaymentNotCreatedError(msg)

            # por agora, não vamos vincular pagamento a nada.
            payment = payment_form.save()

            # ===================== INSTALLMENT ===============================
            if hasattr(transaction, 'group_part_id'):

                part = transaction.group_part
                contract = part.contract

                # Paga parcela
                part.paid = True
                part.save()

                # vincula pagamento à parcela
                payment.part = part
                payment.save()

                # if contract.paid is False and contract.closed is False:
                #     # PRÓXIMA PARCELA
                #     next_part = contract.parts.get(
                #         paid=False,
                #         installment_number=part.installment_number + 1
                #     )
                #
                #     if transaction.payer:
                #         benefactor_id = transaction.payer.benefactor_id
                #     else:
                #         benefactor_id = None
                #
                #     sub_pks = [
                #         str(sub.pk) for sub in transaction.subscriptions.all()
                #     ]
                #
                #     checkout_form = SubscriptionGroupCheckoutForm(data={
                #         'event_pk': event.pk,
                #         'subscription_group_pk':
                #             contract.subscription_group_id,
                #         'group_leader_pk': contract.group_leader_id,
                #         'benefactor_pk': benefactor_id,
                #         'transaction_type': GroupTransaction.BOLETO,
                #         'num_installments': contract.num_installments,
                #         'installment_part_pk': next_part.pk,
                #         'interests_amount': payment_helpers.as_payment_amount(
                #             next_part.interests_amount,
                #         ),
                #         'subscription_pks': ','.join(sub_pks),
                #     })
                #
                #     valid = checkout_form.is_valid()
                #     if valid is False:
                #         raise Exception(checkout_form.errors)
                #
                #     checkout_form.save()

        elif new_status == GroupTransaction.REFUNDED:
            try:
                payment = transaction.payment
                payment.delete()

            except AttributeError:
                pass

            # ===================== INSTALLMENT ===============================
            if transaction.part_id:
                transaction.part.paid = False
                transaction.part.save()

    return transaction
