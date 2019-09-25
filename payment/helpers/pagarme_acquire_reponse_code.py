import logging

from django.conf import settings

from core.helpers import sentry_log


def __notify_error(message, extra_data=None):
    logger = logging.getLogger(__name__)
    logger.error(message, extra=extra_data)


def get_acquire_response(pagarme_transaction_id, code):
    response = get_acquire_response_by_code(code)

    if not response and code is not None:
        response = 'Erro desconhecido.'

        if settings.DEBUG is False:
            msg = response + ' (Código: {}, TransactionID: {}'.format(
                code,
                pagarme_transaction_id
            )
            sentry_log(message=msg, type='warning', notify_admins=True, )

    return response


def get_acquire_response_by_code(code):
    codes = {
        '0000': 'Transação autorizada.',
        '1000': 'Transação não autorizada.',
        '1001': 'Cartão vencido.',
        '1002': 'Transação não permitida.',
        '1003': 'Rejeitado emissor. Procure o banco emissor do cartão.',
        '1004': 'Cartão com restrição. Procure o banco emissor do cartão.',
        '1005': 'Transação não autorizada.',
        '1006': 'Tentativas de senha excedidas.',
        '1007': 'Rejeitado emissor. Procure o banco emissor do cartão.',
        '1008': 'Rejeitado emissor. Procure o banco emissor do cartão.',
        '1009': 'Transação não autorizada.',
        '1010': 'Valor inválido.',
        '1011': 'Cartão inválido.',
        '1013': 'Transação não autorizada.',
        '1014': 'Tipo de conta inválido. Possível transação de crédito em um'
                ' cartão de débito.',
        '1016': 'Saldo insuficiente.',
        '1017': 'Senha inválida.',
        '1019': 'Rejeitado emissor. Procure o banco emissor do cartão.',
        '1020': 'Transação não permitida.',
        '1021': 'Rejeitado pelo emissor. Procure o banco emissor do cartão.',
        '1022': 'Cartão com restrição. Procure o banco emissor do cartão.',
        '1023': 'Rejeitado pelo emissor. Procure o banco emissor do cartão.',
        '1024': 'Transação não permitida.',
        '1025': 'Cartão bloqueado. Procure o banco emissor do cartão.',
        '1042': 'Tipo de conta inválido. Possível transação de crédito em um'
                ' cartão de débito.',
        '1045': 'Código de segurança inválido.',
        '1049': 'Cartão inválido.',
        '2000': 'Cartão com restrição.',
        '2001': 'Cartão vencido.',
        '2002': 'Transação não permitida.',
        '2003': 'Rejeitado emissor. Procure o banco emissor do cartão.',
        '2004': 'Cartão com restrição. Procure o banco emissor do cartão.',
        '2005': 'Transação não autorizada.',
        '2006': 'Tentativas de senha excedidas.',
        '2007': 'Cartão com restrição.',
        '2008': 'Cartão com restrição.',
        '2009': 'Cartão com restrição.',
        '5088': 'Transação não autorizada AmEx. Procure o banco emissor do'
                ' cartão.',
        '5089': 'Erro de comunicação com a operadora.',
        '5091': 'Transação não permitida. Valor da parcela inferior ao mínimo'
                ' permitido. Procure o banco emissor do cartão.',
        '5094': 'Venda com parcelamento não habilitado. Procure o banco'
                ' emissor do cartão.',
        '9102': 'Transação inválida.',
        '9103': 'Transação negada. Procure o banco emissor do cartão.',
        '9108': 'Erro no processamento.',
        '9109': 'Autorização recusada.',
        '9111': 'Time-out na transação.',
        '9112': 'Emissor indisponível.',
        '9124': 'Código de segurança inválido.',
        '9999': 'Erro não especificado.',
    }

    return codes.get(code)
