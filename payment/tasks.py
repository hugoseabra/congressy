import json
import logging
from datetime import datetime

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
from payment.models import Transaction, TransactionStatus

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
        trx = pagarme.transaction.create(data)
    except Exception as e:
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

    amount = payment_helpers.amount_as_decimal(str(trx['amount']))
    liquid_amount = payment_helpers.amount_as_decimal(
        str(data['liquid_amount'])
    )

    if not installments:
        installments = int(trx['installments'])

    # por padrão
    installment_amount = round((amount / installments), 2)

    if trx['payment_method'] == Transaction.BOLETO and installments > 1:
        # Se compra parcelada no boleto, vamos igualar amount e
        # intallment_amount, pois no modelo atual, installment_amount registra
        # o valor da parcela e o amount registra o conjunto de parcelas, o que
        # não faz sentido quando há parcelamento de boleto, sendo o valor
        # transacionado (amount) sempre o valor da parcela.
        installment_amount = amount

    with atomic():

        # ============================ TRANSACTION ========================== #
        transaction = Transaction(
            uuid=data['transaction_id'],
            subscription=subscription,
            data=trx,
            status=trx['status'],
            type=trx['payment_method'],
            date_created=trx['date_created'],
            amount=amount,
            lot_price=subscription.lot.price,
            liquid_amount=liquid_amount,
            installments=installments,
            installment_part=installment_part,
            installment_amount=installment_amount,
        )

        if transaction.type == Transaction.BOLETO:
            boleto_exp_date = trx.get('boleto_expiration_date')
            if boleto_exp_date:
                transaction.boleto_expiration_date = datetime.strptime(
                    boleto_exp_date,
                    "%Y-%m-%dT%H:%M:%S.%fZ"
                )

        if transaction.type == Transaction.CREDIT_CARD:
            card = trx['card']
            transaction.credit_card_holder = card['holder_name']
            transaction.credit_card_first_digits = card['first_digits']
            transaction.credit_card_last_digits = card['last_digits']

        transaction.save()

        TransactionStatus.objects.create(
            transaction=transaction,
            data=trx,
            status=trx['status'],
            date_created=trx['date_created'],
        )

        return transaction


# @TODO create a mock of the response to use during testing
def create_pagarme_organizer_recipient(organization=None):
    if not organization:
        return

    params = {
        'anticipatable_volume_percentage': '100',
        'automatic_anticipation_enabled': 'true',
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
