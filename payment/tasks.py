import json
from decimal import Decimal

import pagarme
from django.conf import settings

from mailer.tasks import send_mail
from payment.exception import TransactionError, OrganizerRecipientError
from payment.models import Transaction, TransactionStatus

pagarme.authentication_key(settings.PAGARME_API_KEY)

congressy_id = settings.PAGARME_RECIPIENT_ID


# @TODO-low create a mock of the response to use during testing
def create_pagarme_transaction(payment=None, subscription=None):
    if not payment or not subscription:
        return

    transaction_instance = Transaction(
        uuid=payment['items'][0]['id'],
        subscription=subscription
    )

    trx = pagarme.transaction.create(payment)

    # @TODO add wrapper here to check if its a dict or a list
    if not isinstance(trx, dict):
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
        """.format(json.dumps(payment), json.dumps(trx))

        send_mail(subject=subject, body=body, to=settings.DEV_ALERT_EMAILS)
        raise TransactionError(message='Unknown API error')

    # Separar centavos
    amount = str(trx['amount'])
    size = len(amount)
    cents = amount[-2] + amount[-1]
    amount = '{}.{}'.format(amount[0:size - 2], cents)
    amount = Decimal(amount)

    transaction_instance.data = trx
    transaction_instance.status = trx['status']
    transaction_instance.type = trx['payment_method']
    transaction_instance.date_created = trx['date_created']
    transaction_instance.amount = amount
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
