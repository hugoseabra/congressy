import pagarme
from django.conf import settings


pagarme.authentication_key(settings.PAGARME_API_KEY)

congressy_id = settings.PAGARME_RECIPIENT_ID


def create_credit_card_transaction(instance=None):

    if not instance:
        return

    # Criar transação.
    params = {

        "amount": instance['price'],

        "card_hash": instance['card_hash'],

        "customer": instance['customer'],

        "billing": instance['billing'],

        "items": [
            {
                "id": "000",
                "title": "Inscrição do Evento: " + instance['event_name'],
                "unit_price": instance['price'],
                "quantity": 1,
                "tangible": False
            }
        ],

        "split_rules": [
            {
                "recipient_id": congressy_id,
                "percentage": 10,
                "liable": True,
                "charge_processing_fee": True
            },
            {
                "recipient_id": instance['recipient_id'],
                "percentage": 90,
                "liable": True,
                "charge_processing_fee": False
            }
        ]

    }

    if settings.DEBUG:
        trx = None
        print('========================= CREDIT CARD TRANSACTION CREATE PARAMS =======================================')
        print(params)
        print('=======================================================================================================')
    else:
        trx = pagarme.transaction.create(params)
        # print(trx)

    return trx


def create_boleto_transaction(instance=None):

    if not instance:
        return

    # Criar transação.
    params = {

        "amount": instance['price'],

        "customer": instance['customer'],
        'payment_method': 'boleto',

        "billing": instance['billing'],

        "items": [
            {
                "id": "000",
                "title": "Inscrição do Evento: " + instance['event_name'],
                "unit_price": instance['price'],
                "quantity": 1,
                "tangible": False
            }
        ],

        "split_rules": [
            {
                "recipient_id": congressy_id,
                "percentage": 10,
                "liable": True,
                "charge_processing_fee": True
            },
            {
                "recipient_id": instance['recipient_id'],
                "percentage": 90,
                "liable": True,
                "charge_processing_fee": False
            }
        ]

    }

    if settings.DEBUG:
        trx = None
        print('========================= BOLETO TRANSACTION CREATE PARAMS ============================================')
        print(params)
        print('=======================================================================================================')
    else:
        trx = pagarme.transaction.create(params)
        # print(trx)

    return trx


def create_payme_back_account(instance=None):

    if not instance:
        return

    params = {
        'agencia': instance['agency'],
        'bank_code': instance['bank_code'],
        'conta': instance['account'],
        'document_number': instance['cnpj_ou_cpf'],
        'legal_name': instance['legal_name'],
        'type': instance['account_type'],
    }

    if 'agencia_dv' in instance:
        params['agencia_dv'] = instance['agencia_dv']

    if 'conta_dv' in instance:
        params['conta_dv'] = instance['conta_dv']

    if settings.DEBUG:
        bank_account = None
        print('========================= BANK ACCOUNT CREATE PARAMS ==================================================')
        print(params)
        print('=======================================================================================================')
    else:
        # Cria uma "conta bancaria" no sistema pagar.me
        bank_account = pagarme.bank_account.create(params)

    return bank_account


def create_payme_recipient(bank_account=None):

    if not bank_account:
        return

    params = {
        'anticipatable_volume_percentage': '80',
        'automatic_anticipation_enabled': 'false',
        'transfer_day': '5',
        'transfer_enabled': 'true',
        'transfer_interval': 'weekly',
        'bank_account': bank_account,
    }

    if settings.DEBUG:
        recipient = None
        print('========================= PAGARME RECEBEDOR CREATE PARAMS =============================================')
        print(params)
        print('=======================================================================================================')
    else:
        # Cria uma "recebedor" no sistema pagar.me
        recipient = pagarme.recipient.create(params)

    return recipient
