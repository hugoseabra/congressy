from datetime import datetime, timedelta
from decimal import Decimal

from payment.models import Transaction


def event_starts_in(now: datetime):
    pass


def get_opened_boleto_transactions(subscription):
    """ Verifica se inscrição possui boletos que ainda não venceram. """

    now = datetime.now()

    return Transaction.objects.filter(
        subscription_id=subscription.pk,
        lot__event_id=subscription.event_id,
        type=Transaction.BOLETO,
        boleto_expiration_date__gt=now.date(),
    ).exclude(
        status__in=[
            Transaction.PAID,
            Transaction.REFUNDED,
            Transaction.REFUSED,
        ],
    )


def has_open_boleto(subscription):
    return get_opened_boleto_transactions(subscription).count()


def is_boleto_allowed(event):
    """
    Verifica se evento permite transações com boleto.
    """
    days_boleto = timedelta(days=event.boleto_limit_days)

    # Data/hora em que os boletos serão desativados.
    diff_days_boleto = event.date_start - days_boleto

    # Se evento permite boletos mediante configuração de mínimo de dias
    # de emissão de boleto configurado em 'boleto_limit_days'

    return datetime.now() < diff_days_boleto


def amount_as_decimal(amount):
    """ Converte um montante processável com meio de pagamento para Decimal """
    if isinstance(amount, Decimal):
        return amount

    if amount is None:
        return amount

    # Separar centavos
    amount = str(amount)
    size = len(amount)
    if size >= 3:
        cents = amount[-2] + amount[-1]
        amount = '{}.{}'.format(amount[0:size - 2], cents)
    elif size == 2:
        cents = amount[-2] + amount[-1]
        amount = '{}.{}'.format(0, cents)
    else:
        amount = '{}.{}{}'.format(0, 0, amount)

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
