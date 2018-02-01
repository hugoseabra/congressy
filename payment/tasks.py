import pagarme
from django.conf import settings


pagarme.authentication_key(settings.PAGARME_API_KEY)

congressy_id = settings.PAGARME_RECIPIENT_ID


def create_credit_card_transaction(payment=None):

    if not payment:
        return

    # Criar transação.
    params = {

        "amount": payment['price'],

        "card_hash": payment['card_hash'],

        "customer": payment['customer'],

        "billing": payment['billing'],

        "items": [
            {
                "id": "000",
                "title": "Inscrição do Evento: " + payment['event_name'],
                "unit_price": payment['price'],
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
                "recipient_id": payment['recipient_id'],
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


def create_boleto_transaction(payment=None):

    if not payment:
        return

    # Criar transação.
    params = {

        "amount": payment['price'],

        "customer": payment['customer'],
        'payment_method': 'boleto',

        "billing": payment['billing'],

        "items": [
            {
                "id": "000",
                "title": "Inscrição do Evento: " + payment['event_name'],
                "unit_price": payment['price'],
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
                "recipient_id": payment['recipient_id'],
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


def create_payme_back_account(payment=None):

    if not payment:
        return

    params = {
        'agencia': payment['agency'],
        'bank_code': payment['bank_code'],
        'conta': payment['account'],
        'document_number': payment['cnpj_ou_cpf'],
        'legal_name': payment['legal_name'],
        'type': payment['account_type'],
    }

    if 'agencia_dv' in payment:
        params['agencia_dv'] = payment['agencia_dv']

    if 'conta_dv' in payment:
        params['conta_dv'] = payment['conta_dv']

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
