import pagarme
from django.conf import settings


pagarme.authentication_key(settings.PAGARME_API_KEY)


def create_credit_card_transaction(instance=None):

    if not instance:
        return

    congressy_id = 're_cjcupb1iq0200zl6d89r92s32'

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

    trx = pagarme.transaction.create(params)
    # print(trx)

    return trx


def create_boleto_transaction(instance=None):

    if not instance:
        return

    congressy_id = 're_cjcupb1iq0200zl6d89r92s32'

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

    trx = pagarme.transaction.create(params)

    #  print(trx)

    return trx


def create_payme_back_account(instance):

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

    # Cria uma "recebedor" no sistema pagar.me
    recipient = pagarme.recipient.create(params)

    return recipient
