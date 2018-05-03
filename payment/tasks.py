import json
from decimal import Decimal
from datetime import datetime

import pagarme
from django.conf import settings

from mailer.tasks import send_mail
from payment.exception import (
    OrganizerRecipientError,
    RecipientError,
    TransactionError,
)
from payment.models import Transaction, TransactionStatus

pagarme.authentication_key(settings.PAGARME_API_KEY)

congressy_id = settings.PAGARME_RECIPIENT_ID


def separate_amount(amount):
    amount = str(amount)
    size = len(amount)
    cents = amount[-2] + amount[-1]
    amount = '{}.{}'.format(amount[0:size - 2], cents)
    return Decimal(amount)


# @TODO-low create a mock of the response to use during testing
def create_pagarme_transaction(transaction_data, subscription=None):
    payment = transaction_data.get_data()
    liquid_amount = transaction_data.liquid_amount

    if not payment or not subscription:
        return

    transaction_instance = Transaction(
        uuid=payment['items'][0]['id'],
        subscription=subscription
    )

    try:

        trx = pagarme.transaction.create(payment)

    except Exception as e:
        # @TODO add wrapper here to check if its a dict or a list
        # @TODO trigger do
        subject = "Erro ao criar transação: Unknown API error"
        body = """
            Erro ao criar transação:
            
            <br/>
            
            Transação: 
            <br />
            
            <pre><code>{0}</code></pre>
            <br />
            Erro:
            <br/> 
            
            <pre><code>{1}</code></pre>
        """.format(json.dumps(payment), str(e))

        send_mail(subject=subject, body=body, to=settings.DEV_ALERT_EMAILS)
        raise TransactionError(message='Unknown API error')

    # Separar centavos
    items = trx['items']
    subscription = items.pop(0)

    transaction_instance.data = trx
    transaction_instance.status = trx['status']
    transaction_instance.type = trx['payment_method']
    transaction_instance.date_created = trx['date_created']
    transaction_instance.subscription_amount = subscription['unit_price']/100
    transaction_instance.subscription_liquid_amount = liquid_amount
    optional_total = 0

    for item in items:
        optional_total += item['unit_price']/100

    # @TODO add optional liquid amount and seperate cents

    transaction_instance.optional_amount = optional_total

    if transaction_instance.type == Transaction.BOLETO:
        boleto_exp_date = trx.get('boleto_expiration_date')
        if boleto_exp_date:
            transaction_instance.boleto_expiration_date = datetime.strptime(
                boleto_exp_date,
                "%Y-%m-%dT%H:%M:%S.%fZ"
            )

    transaction_instance.save()

    transaction_status = TransactionStatus(
        transaction=transaction_instance,
        data=trx
    )

    transaction_status.data['status'] = trx['status']
    transaction_status.date_created = trx['date_created']
    transaction_status.status = trx['status']
    transaction_status.save()


# @TODO create a mock of the response to use during testing
def create_pagarme_organizer_recipient(organization=None):
    if not organization:
        return

    params = {
        'anticipatable_volume_percentage': '80',
        'automatic_anticipation_enabled': 'false',
        'transfer_day': '5',
        'transfer_enabled': 'true',
        'transfer_interval': 'weekly',
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
        'anticipatable_volume_percentage': '80',
        'automatic_anticipation_enabled': 'false',
        'transfer_day': '5',
        'transfer_enabled': 'true',
        'transfer_interval': 'weekly',
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
