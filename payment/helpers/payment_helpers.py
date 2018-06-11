from datetime import datetime, timedelta
from decimal import Decimal

from payment.models import Transaction


def get_opened_boleto_transactions(subscription):
    """ Verifica se inscrição possui boletos que ainda não venceram. """

    now = datetime.now()

    return Transaction.objects.filter(
        subscription=subscription,
        lot__event=subscription.event,
        type=Transaction.BOLETO,
        boleto_expiration_date__gt=now.date(),
    ).exclude(
        status__in=[Transaction.PAID, Transaction.PROCESSING],
    )


def is_boleto_allowed(event):
    """
    Verifica se evento permite transações com boleto.
    """
    days_boleto = timedelta(days=event.boleto_limit_days)

    # Data/hora em que os boletos serão desativados.
    diff_days_boleto = datetime.now() - days_boleto

    # Se evento permite boletos mediante configuração de mínimo de dias
    # de emissão de boleto configurado em 'boleto_limit_days'
    return event.date_start >= diff_days_boleto


def amount_as_decimal(amount):
    """ Converte um montante processável com meio de pagamento para Decimal """
    if isinstance(amount, Decimal):
        return amount

    if amount is None:
        return amount

    # Separar centavos
    amount = str(amount)
    size = len(amount)
    cents = amount[-2] + amount[-1]
    amount = '{}.{}'.format(amount[0:size - 2], cents)
    return round(Decimal(amount), 2)


def decimal_processable_amount(value):
    """
    Converte um valor Decimalprocessável para um montante a ser usado por
    meios de pagamento
    """
    if not isinstance(value, Decimal):
        value = Decimal(value)

    value = str(round(value, 2))
    v_split = value.split('.')
    value = v_split[0]
    cents = v_split[1] if len(v_split) == 2 else ''
    return str(value + cents)
