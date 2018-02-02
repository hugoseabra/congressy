import pagarme
from django.conf import settings

from payment.models import Transaction

pagarme.authentication_key(settings.PAGARME_API_KEY)

congressy_id = settings.PAGARME_RECIPIENT_ID


# @TODO create a mock of the response to use during testing
def create_pagarme_transaction(payment=None, subscription=None):

    if not payment or not subscription:
        return

    transaction_instance = Transaction(
        uuid=payment['items'][0]['id'],
        subscription=subscription
    )

    trx = pagarme.transaction.create(payment)

    # @TODO add wrapper here to check if its a dict or a list

    transaction_instance.data = trx
    transaction_instance.save()


# @TODO create a mock of the response to use during testing
def create_pagarme_recipient(organization=None):
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

    organization.bank_account_id = recipient['bank_account']['id']
    organization.document_type = recipient['bank_account']['document_type']
    organization.recipient_id = recipient['id']
    organization.date_created = recipient['bank_account']['date_created']
    organization.active_recipient = True

    organization.save()
