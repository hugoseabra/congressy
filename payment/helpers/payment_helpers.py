from datetime import datetime, timedelta
from decimal import Decimal

from django.conf import settings

from gatheros_event.models import Event
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
    return get_opened_boleto_transactions(subscription).count() > 0


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


def as_payment_format(value):
    return decimal_processable_amount(value)


def as_payment_amount(value):
    """
    Converte um valor Decimal processável para um montante a ser usado por
    meios de pagamento
    """
    if not isinstance(value, Decimal):
        value = Decimal(value)

    value = str(round(value, 2))
    v_split = value.split('.')
    value = v_split[0]
    cents = v_split[1] if len(v_split) == 2 else ''
    return str(value + cents)


def get_liquid_amount(event: Event, amount: Decimal):
    cgsy_percent = Decimal(event.congressy_percent)
    if cgsy_percent > 0:
        cgsy_percent = cgsy_percent / 100

    mininum_amount = Decimal(settings.CONGRESSY_MINIMUM_AMOUNT)

    congressy_amount = amount * cgsy_percent
    if congressy_amount < mininum_amount:
        congressy_amount = mininum_amount

    return amount - congressy_amount


def get_amounts_from_transaction(event: Event, amount: Decimal):
    cgsy_percent_amount = Decimal(event.congressy_percent)
    cgsy_percent = cgsy_percent_amount / 100

    mininum_amount = Decimal(settings.CONGRESSY_MINIMUM_AMOUNT)

    if event.transfer_tax is True:
        # Se houver transferência de taxa, quer dizer que o montante
        # transacionado representa mais de 100% do valor original. Neste caso,
        # temos de encontrar o valor original.
        proportional_percent = 1 + cgsy_percent

        liquid_amount = amount / proportional_percent
        congressy_amount = amount - liquid_amount

        if congressy_amount < mininum_amount:
            congressy_amount = mininum_amount
            liquid_amount = amount - congressy_amount
    else:
        congressy_amount = amount * cgsy_percent

        if congressy_amount < mininum_amount:
            congressy_amount = mininum_amount

        liquid_amount = amount - congressy_amount

    return {
        'transfer_tax': event.transfer_tax,
        'congressy_percent': cgsy_percent,
        'amount': amount,
        'liquid_amount': liquid_amount,
        'congressy_amount': congressy_amount,
    }
