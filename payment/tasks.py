import pagarme
from django.conf import settings
from payment.models import Transaction

pagarme.authentication_key(settings.PAGARME_API_KEY)

congressy_id = settings.PAGARME_RECIPIENT_ID


def create_pagarme_transaction(payment=None):
    if not payment:
        return

    # Criar transação.
    if settings.DEBUG:

        # mock of the response to use during testing
        trx = {'object': 'transaction',
               'status': 'waiting_payment',
               'refuse_reason': None,
               'status_reason': 'acquirer',
               'acquirer_response_code': None,
               'acquirer_name': 'pagarme',
               'acquirer_id': '5a25880b88cc48ba7f20668a',
               'authorization_code': None,
               'soft_descriptor': None,
               'tid': 2849344,
               'nsu': 2849344,
               'date_created': '2018-02-01T21:39:46.172Z',
               'date_updated': '2018-02-01T21:39:46.731Z',
               'amount': 14500,
               'authorized_amount': 14500,
               'paid_amount': 0,
               'refunded_amount': 0,
               'installments': 1,
               'id': 2849344,
               'cost': 0,
               'card_holder_name': None,
               'card_last_digits': None,
               'card_first_digits': None,
               'card_brand': None,
               'card_pin_mode': None,
               'postback_url': None,
               'payment_method': 'boleto', 'capture_method': 'ecommerce',
               'antifraud_score': None,
               'boleto_url': 'https://pagar.me',
               'boleto_barcode': '1234 5678',
               'boleto_expiration_date': '2018-02-03T02:00:00.000Z',
               'referer': 'api_key',
               'ip': '187.32.44.44',
               'subscription_id': None,
               'phone': None,
               'address': None,
               'customer': {'object': 'customer', 'id': 468931, 'external_id': None, 'type': 'individual',
                            'country': 'br',
                            'document_number': None, 'document_type': 'cpf', 'name': 'Hugo Seabra Batista',
                            'email': 'hugoseabra19@gmail.com', 'phone_numbers': ['+556296550852'], 'born_at': None,
                            'birthday': '1983-01-22', 'gender': None, 'date_created': '2018-02-01T21:39:46.103Z',
                            'documents': [{'object': 'document', 'id': 'doc_cjd50xl5n039qmy6eiqsxi0bp', 'type': 'cpf',
                                           'number': '00177542160'}]},
               'billing': {
                   'address': {'object': 'address', 'street': 'Rua Santos Dumont', 'complementary': None,
                               'street_number': 'None', 'neighborhood': 'Vila Lucimar', 'city': 'Goiânia',
                               'state': 'go',
                               'zipcode': '75400000', 'country': 'br', 'id': 275246}, 'object': 'billing', 'id': 28567,
                   'name': 'Hugo Seabra Batista'},
               'shipping': None,
               'items': [
                   {'object': 'item', 'id': '000', 'title': 'Inscrição do Evento: /MNT', 'unit_price': 14500,
                    'quantity': 1,
                    'category': None, 'tangible': False, 'venue': None, 'date': None
                    }],
               'card': None,
               'split_rules': [
                {'object': 'split_rule', 'id': 'sr_cjd50xl72039smy6ewsqahb0g', 'liable': True, 'amount': None,
                 'percentage': 90, 'recipient_id': 're_cjd4y7z9p03bnog6dxm88bxpw', 'charge_remainder': False,
                 'charge_processing_fee': False, 'date_created': '2018-02-01T21:39:46.190Z',
                 'date_updated': '2018-02-01T21:39:46.190Z'},
                {'object': 'split_rule', 'id': 'sr_cjd50xl71039rmy6eejsrjbc2', 'liable': True, 'amount': None,
                 'percentage': 10, 'recipient_id': 're_cjcupb1iq0200zl6d89r92s32', 'charge_remainder': True,
                 'charge_processing_fee': True, 'date_created': '2018-02-01T21:39:46.190Z',
                 'date_updated': '2018-02-01T21:39:46.190Z'}], 'metadata': {}, 'antifraud_metadata': {},
               'reference_key': None, 'device': None, 'local_transaction_id': None, 'local_time': None,
               'fraud_covered': False}
    else:
        trx = pagarme.transaction.create(payment)

    trx = pagarme.transaction.create(payment)

    return trx


# @TODO create a mock of the responose to use during testing
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

    if settings.DEBUG:
        recipient = None
        print('========================= PAGARME RECEBEDOR CREATE PARAMS =============================================')
        print(params)
        print('=======================================================================================================')
    else:
        # Cria uma "recebedor" no sistema pagar.me
        recipient = pagarme.recipient.create(params)
    # @TODO remove this!!!!!!!
    # @TODO add wrapper to generate exceptions here.
    recipient = pagarme.recipient.create(params)

    organization.bank_account_id = recipient['bank_account']['id']
    organization.recipient_id = recipient['id']
    organization.active_recipient = True

    organization.save()
