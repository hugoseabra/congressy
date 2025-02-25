import json
import logging
from datetime import datetime
from pprint import pprint

import pagarme
from django.conf import settings
from django.db.transaction import atomic

from mailer.tasks import send_mail
from payment.exception import (
    OrganizerRecipientError,
    RecipientError,
    TransactionApiError,
)
from payment.helpers import payment_helpers
from payment.models import Transaction, TransactionStatus, SplitRule
from payment.pagarme_sdk.transaction import get_split_rules
from payment.payable.updater import update_payables

pagarme.authentication_key(settings.PAGARME_API_KEY)

congressy_id = settings.PAGARME_RECIPIENT_ID


def __notify_error(message, extra_data=None):
    logger = logging.getLogger(__name__)
    logger.error(message, extra=extra_data)


# @TODO create a mock of the response to use during testing
def create_pagarme_transaction(subscription,
                               data,
                               installments=None,
                               installment_part=None):
    try:
        trans_trx = pagarme.transaction.create(data)
        split_rules_trx = get_split_rules(trans_trx['id'])

    except Exception as e:

        pprint(e)
        pprint(data)

        errors_msg = []
        if hasattr(e, 'args'):
            errors = [errs for errs in e.args]
            for error in errors[0]:
                if isinstance(error, dict):
                    errors_msg.append('{}: {}'.format(
                        error.get('parameter_name'),
                        error.get('message'),
                    ))
                else:
                    errors_msg.append(error)
        else:
            errors_msg.append(e)

        msg = 'Pagar.me: erro de transação: {}'.format(";".join(errors_msg))
        __notify_error(message=msg, extra_data=data)
        raise TransactionApiError(
            'Algo deu errado com a comunicação com o provedor de pagamento.'
        )

    """
    Montante da transação pode ser:
    
    SE BOLETO:
    - TOTAL: se parcelamento for igual a 1, pois não o pagamento é integral;
    - PARCIAL: se parcelamento for mais do que 1, pois o montante transacionado
    equivale apenas à parcela de pagamento;
    
    SE CARTÃO:
    - TOTAL: independente do parcelamento, pois o parcelamento de cartão é
    controlado pelo provedor de pagamento e, por sua vez, pela bandeira do
    cartão;
    """

    amount = payment_helpers.amount_as_decimal(str(trans_trx['amount']))
    liquid_amount = payment_helpers.amount_as_decimal(
        str(data['liquid_amount'])
    )

    if not installments:
        installments = int(trans_trx['installments'])

    # por padrão
    installment_amount = round((amount / installments), 2)

    if trans_trx['payment_method'] == Transaction.BOLETO and installments > 1:
        # Se compra parcelada no boleto, vamos igualar amount e
        # intallment_amount, pois no modelo atual, installment_amount registra
        # o valor da parcela e o amount registra o conjunto de parcelas, o que
        # não faz sentido quando há parcelamento de boleto, sendo o valor
        # transacionado (amount) sempre o valor da parcela.
        installment_amount = amount

    with atomic():

        created = datetime.strptime(
            trans_trx['date_created'],
            "%Y-%m-%dT%H:%M:%S.%fZ"
        )

        # ============================ TRANSACTION ========================== #
        transaction = Transaction(
            uuid=data['transaction_id'],
            subscription=subscription,
            data=trans_trx,
            status=trans_trx['status'],
            type=trans_trx['payment_method'],
            date_created=created,
            amount=amount,
            lot_price=subscription.lot.price,
            liquid_amount=liquid_amount,
            installments=installments,
            installment_part=installment_part,
            installment_amount=installment_amount,
            pagarme_id=trans_trx['id'],
        )

        if transaction.type == Transaction.BOLETO:
            boleto_exp_date = trans_trx.get('boleto_expiration_date')
            if boleto_exp_date:
                transaction.boleto_expiration_date = datetime.strptime(
                    boleto_exp_date,
                    "%Y-%m-%dT%H:%M:%S.%fZ"
                )

        if transaction.type == Transaction.CREDIT_CARD:
            card = trans_trx['card']
            transaction.credit_card_holder = card['holder_name']
            transaction.credit_card_first_digits = card['first_digits']
            transaction.credit_card_last_digits = card['last_digits']

        transaction.save()

        TransactionStatus.objects.create(
            transaction=transaction,
            data=trans_trx,
            status=trans_trx['status'],
            date_created=trans_trx['date_created'],
        )

    with atomic():

        for sr in split_rules_trx:

            fee_resp = sr['charge_processing_fee']
            amount = payment_helpers.amount_as_decimal(str(sr['amount']))

            created = datetime.strptime(
                sr['date_created'],
                "%Y-%m-%dT%H:%M:%S.%fZ"
            )

            split_rule = SplitRule.objects.create(
                transaction=transaction,
                pagarme_id=sr['id'],
                is_congressy=fee_resp is True,
                charge_processing_fee=fee_resp is True,
                amount=amount,
                recipient_id=sr['recipient_id'],
                created=created,
            )

            update_payables(split_rule)

        return transaction


# @TODO create a mock of the response to use during testing
def create_pagarme_organizer_recipient(organization=None):
    if not organization:
        return

    # @TODO: RECIPIENT POSSUEM POSTBACKS - IMPLEMENTAR
    params = {
        'transfer_enabled': 'true',
        'automatic_anticipation_enabled': 'true',
        'transfer_interval': 'weekly',
        'anticipatable_volume_percentage': '100',
        'transfer_day': '5',
        'automatic_anticipation_type': '1025',
        'automatic_anticipation_days': '[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,'
                                       '16,17,18,19,20,21,22,23,24,25,26,27,'
                                       '28,29,30,31]',
        'automatic_anticipation_1025_delay': '30',
        'bank_account': {
            'agencia': organization.agency,
            'bank_code': organization.bank_code,
            'conta': organization.account,
            'conta_dv': organization.conta_dv,
            'document_number': organization.cnpj_ou_cpf,
            'legal_name': organization.legal_name,
            'type': organization.account_type,
        },
    }

    if organization.agencia_dv:
        params['bank_account'].update(
            {'agencia_dv': organization.agencia_dv})

    recipient = pagarme.recipient.create(params)

    # @TODO add wrapper here to check if its a dict or a list
    if not isinstance(recipient, dict):
        subject = "Erro ao criar conta de organizador: Unknown API error"
        body = """
            Erro ao criar conta de organizador:

            <br/>

            Organização: {0} 
            <br />
            Erro:
            <br/> 
            <pre><code>{1}</code></pre>
        """.format(organization.name, json.dumps(recipient))

        send_mail(subject=subject, body=body, to=settings.DEV_ALERT_EMAILS)
        raise OrganizerRecipientError(message='Unknown API error')

    organization.bank_account_id = recipient['bank_account']['id']
    organization.document_type = recipient['bank_account']['document_type']
    organization.recipient_id = recipient['id']
    organization.date_created = recipient['bank_account']['date_created']
    organization.active_recipient = True

    organization.save()


def create_pagarme_recipient(recipient_dict):
    params = {
        'transfer_enabled': 'true',
        'automatic_anticipation_enabled': 'true',
        'transfer_interval': 'weekly',
        'anticipatable_volume_percentage': '100',
        'transfer_day': '5',
        'automatic_anticipation_type': '1025',
        'automatic_anticipation_days': '[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,'
                                       '16,17,18,19,20,21,22,23,24,25,26,27,'
                                       '28,29,30,31]',
        'automatic_anticipation_1025_delay': '30',
        'bank_account': {
            'agencia': recipient_dict['agencia'],
            'bank_code': recipient_dict['bank_code'],
            'conta': recipient_dict['conta'],
            'conta_dv': recipient_dict['conta_dv'],
            'document_number': recipient_dict['document_number'],
            'legal_name': recipient_dict['legal_name'],
            'type': recipient_dict['type'],
        },
    }

    if recipient_dict.get('agencia_dv'):
        params['bank_account'].update(
            {'agencia_dv': recipient_dict.get('agencia_dv')})

    # @TODO tratar exceção tanto de comunicação quanto de dados.
    recipient = pagarme.recipient.create(params)

    # @TODO add wrapper here to check if its a dict or a list
    if not isinstance(recipient, dict):
        subject = "Erro ao criar conta: Unknown API error"
        body = """
            Erro ao criar conta:

            <br/>

            Recipiente: {0} 
            <br />
            Erro:
            <br/> 
            <pre><code>{1}</code></pre>
        """.format(recipient_dict['name'], json.dumps(recipient))

        send_mail(subject=subject, body=body, to=settings.DEV_ALERT_EMAILS)
        raise RecipientError(message='Unknown API error')

    return recipient


def fetch_transaction(pagarme_transaction_id) -> dict:
    try:
        return pagarme.transaction.find_by_id(pagarme_transaction_id)

    except Exception as e:
        print(e)
        return dict()
