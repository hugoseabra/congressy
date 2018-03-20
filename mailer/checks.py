from mailer import exception


def check_notification_transaction_unpaid_boleto(transaction):
    """
    Verifica notificação de transação não-paga do tipo 'boleto'

    - inscrição não pode estar como 'confirmada';
    - transação deve ser do tipo 'boleto';
    - transação não pode estar com status de 'paga';
    - transação deve ter a URL do boleto para a notificação.
    """
    _check_unpaid_transaction(transaction)

    if transaction.type != transaction.BOLETO:
        raise exception.NotifcationError(
            "Tipo de transação inválido para esta notificação: '{type}'. Esta"
            " notificação é para transações do tipo '{boleto}'".format(
                type=transaction.type,
                boleto=transaction.BOLETO
            )
        )

    if not transaction.boleto_url:
        raise exception.NotifcationError(
            "URL de boleto não encontrada. Transação não pode ser realizada"
            " sem a URL do boleto."
        )


def check_notification_transaction_paid_boleto(transaction):
    """
    Verifica notificação de transação paga do tipo 'boleto'

    - inscrição deve estar como 'confirmada';
    - transação deve ser do tipo 'boleto';
    - transação deve pode estar com status de 'paga';
    """
    _check_paid_transaction(transaction)

    if transaction.type != transaction.BOLETO:
        raise exception.NotifcationError(
            "Tipo de transação inválido para esta notificação: '{type}'. Esta"
            " notificação é para transações do tipo '{boleto}'".format(
                type=transaction.type,
                boleto=transaction.BOLETO
            )
        )


def check_notification_transaction_unpaid_credit_card(transaction):
    """
    Verifica notificação de transação não-paga do tipo 'credit_card'

    - inscrição não pode estar como 'confirmada';
    - transação deve ser do tipo 'credit_card';
    - transação não pode estar com status de 'paga';
    """
    _check_unpaid_transaction(transaction)

    if transaction.type != transaction.CREDIT_CARD:
        raise exception.NotifcationError(
            "Tipo de transação inválido para esta notificação: '{type}'. Esta"
            " notificação é para transações do tipo '{cc}'".format(
                type=transaction.type,
                cc=transaction.CREDIT_CARD
            )
        )


def check_notification_transaction_paid_credit_card(transaction):
    """
    Verifica notificação de transação paga do tipo 'credit_card'

    - inscrição deve estar como 'confirmada';
    - transação deve ser do tipo 'credit_card';
    - transação deve pode estar com status de 'paga';
    """
    _check_paid_transaction(transaction)

    if transaction.type != transaction.CREDIT_CARD:
        raise exception.NotifcationError(
            "Tipo de transação inválido para esta notificação: '{type}'. Esta"
            " notificação é para transações do tipo '{cc}'".format(
                type=transaction.type,
                cc=transaction.CREDIT_CARD
            )
        )


def check_notification_transaction_refused_credit_card(transaction):
    """
    Verifica notificação de transação paga do tipo 'credit_card'

    - inscrição deve estar como 'confirmada';
    - transação deve ser do tipo 'credit_card';
    - transação deve pode estar com status de 'paga';
    """
    _check_refused_transaction(transaction)

    if transaction.type != transaction.CREDIT_CARD:
        raise exception.NotifcationError(
            "Tipo de transação inválido para esta notificação: '{type}'. Esta"
            " notificação é para transações do tipo '{cc}'".format(
                type=transaction.type,
                cc=transaction.CREDIT_CARD
            )
        )


def _check_unpaid_transaction(transaction):
    """ Verifica transações não pagas. """
    subscription = transaction.subscription

    if subscription.status == subscription.CONFIRMED_STATUS:
        raise exception.NotifcationError(
            "Notificação de inscrição não-paga só poderá ser feita se"
            " inscrição não estiver confirmada. Esta inscrição já está"
            " confirmada."
        )

    if transaction.status == transaction.PAID:
        raise exception.NotifcationError(
            "Transação já está paga. A notificação é somente para transação"
            " que não foi paga."
        )


def _check_paid_transaction(transaction):
    """ Verifica transações pagas. """
    subscription = transaction.subscription

    if subscription.status != subscription.CONFIRMED_STATUS:
        raise exception.NotifcationError(
            "Notificação de inscrição paga só poderá ser feita se inscrição"
            " estiver confirmada. Esta inscrição não está confirmada."
        )

    if transaction.status != transaction.PAID:
        raise exception.NotifcationError(
            "Transação ainda não está paga. A notificação é somente para"
            " transação paga."
        )


def _check_refused_transaction(transaction):
    """ Verifica transações pagas e recusadas. """
    subscription = transaction.subscription

    if subscription.status != subscription.AWAITING_STATUS:
        raise exception.NotifcationError(
            "Notificação de inscrição recusada só poderá ser feita se"
            " inscrição estiver pendete. Esta inscrição não está pendente."
        )

    if transaction.status == transaction.PAID:
        raise exception.NotifcationError(
            "Transação ainda já está paga. A notificação é somente para"
            " transação recusada."
        )