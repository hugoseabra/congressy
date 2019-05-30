from decimal import Decimal

from django.conf import settings

from payment.installments import Calculator as InstallmentCalculator


def get_max_installments_allowed_for_price(price):
    """
    Regra: Não permitir parcelamento com preços de parcela abaixo de 25$.
           Preço do lote mínimo 250$ sem juros.

    :param price:
    :return:
    """

    if not isinstance(price, Decimal):
        price = Decimal(price)

    minimum_amount_for_installments = \
        Decimal(settings.CONGRESSY_MINIMUM_AMOUNT_FOR_INSTALLMENTS)

    max_installments_allowed = price / minimum_amount_for_installments

    if max_installments_allowed > 10:
        max_installments_allowed = 10
    elif max_installments_allowed < 1:
        max_installments_allowed = 0

    return int(max_installments_allowed)


# ====================== API HELPERS ==========================================

def get_lot_price_for_audience(raw_price, cgsy_percent, transfer_tax):
    """

    Visualizar valor final destinado ao participante (a pagar).

    :param raw_price:
    :param cgsy_percent:
    :param transfer_tax:
    :return:
    """
    if not isinstance(raw_price, Decimal):
        raw_price = Decimal(raw_price)

    percent = Decimal(cgsy_percent) / Decimal(100)
    cgsy_min = Decimal(settings.CONGRESSY_MINIMUM_AMOUNT)

    congressy_cut = Decimal(raw_price) * percent
    if cgsy_min > congressy_cut:
        congressy_cut = cgsy_min

    if transfer_tax:
        audience_price = raw_price + congressy_cut
    else:
        audience_price = raw_price

    return audience_price


def get_lot_price_for_organizer(raw_price, cgsy_percent, transfer_tax):
    """

    Visualizar valor final destinado ao organizador (a receber)

    :param raw_price:
    :param cgsy_percent:
    :param transfer_tax:
    :return:
    """

    if not isinstance(raw_price, Decimal):
        raw_price = Decimal(raw_price)

    percent = Decimal(cgsy_percent) / Decimal(100)
    cgsy_min = Decimal(settings.CONGRESSY_MINIMUM_AMOUNT)

    congressy_cut = Decimal(raw_price) * percent
    if cgsy_min > congressy_cut:
        congressy_cut = cgsy_min

    if transfer_tax:
        organizer_amount = raw_price
    else:
        organizer_amount = raw_price - congressy_cut

    return organizer_amount


def get_lot_installment_prices_for_audience(price, cgsy_percent,
                                            installments, free_installments,
                                            transfer_tax):
    """
    Visualizar detalhamento(uma lista) de valores de parcelas para o
    participante.

    :param price:
    :param cgsy_percent:
    :param installments:
    :param free_installments:
    :param transfer_tax:
    :return:
    """

    if not isinstance(price, Decimal):
        price = Decimal(price)

    if not isinstance(cgsy_percent, Decimal):
        cgsy_percent = Decimal(cgsy_percent)

    interests_rate = Decimal(
        Decimal(settings.CONGRESSY_INSTALLMENT_INTERESTS_RATE) / Decimal(100)
    )

    calculator = InstallmentCalculator(
        interests_rate=interests_rate,
        total_installments=installments,
        free_installments=free_installments,
    )

    percent = cgsy_percent / Decimal(100)
    cgsy_min = Decimal(settings.CONGRESSY_MINIMUM_AMOUNT)
    congressy_cut = price * percent
    if cgsy_min > congressy_cut:
        congressy_cut = cgsy_min

    if transfer_tax:
        price = price + congressy_cut

    audience_prices_list = dict()
    installment_prices = calculator.get_installment_prices(price)

    counter = 1
    for p in installment_prices:
        if counter == 1:
            counter += 1
            continue

        audience_prices_list[counter] = round(p, 3)
        counter += 1

    return audience_prices_list


def get_lot_installment_prices_for_organizer(price, cgsy_percent,
                                             installments, free_installments,
                                             transfer_tax):
    """

    Visualizar detalhamento(uma lista) de valores de parcelas para o
    organizador.

    :param price:
    :param cgsy_percent:
    :param installments:
    :param free_installments:
    :param transfer_tax:
    :return:
    """

    if not isinstance(price, Decimal):
        price = Decimal(price)

    if not isinstance(cgsy_percent, Decimal):
        cgsy_percent = Decimal(cgsy_percent)

    interests_rate = Decimal(
        Decimal(settings.CONGRESSY_INSTALLMENT_INTERESTS_RATE) / Decimal(100)
    )

    calculator = InstallmentCalculator(
        interests_rate=interests_rate,
        total_installments=installments,
        free_installments=free_installments,
    )

    percent = cgsy_percent / Decimal(100)
    cgsy_min = Decimal(settings.CONGRESSY_MINIMUM_AMOUNT)
    congressy_cut = price * percent
    if cgsy_min > congressy_cut:
        congressy_cut = cgsy_min

    liquid_price = price

    if transfer_tax:
        price = price + congressy_cut

    interests_amounts = calculator.get_liquid_interest_prices(price)

    organizer_price_lists = dict()

    counter = 1
    for interests_amount in interests_amounts:
        if counter == 1:
            counter += 1
            continue

        if counter <= free_installments:
            organizer_price_lists[counter] = round(
                liquid_price - Decimal(interests_amount),
                3
            )
        else:
            organizer_price_lists[counter] = round(liquid_price, 3)

        counter += 1

    return organizer_price_lists