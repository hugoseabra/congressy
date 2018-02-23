""" Helper para inscrições. """
import locale
from datetime import datetime

from openpyxl import Workbook
from six import BytesIO

from payment.models import TransactionStatus

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')


def export_event_data(event):
    """
    Exportação do queryset de inscrições em formato xlsx

    :param event:
    :return: ByteIO
    """
    stream = BytesIO()

    wb = Workbook()

    ws1 = wb.active
    ws1.title = 'Participantes'

    _export_subscriptions(ws1, event.subscriptions.all())

    has_paid_lots = False
    for lot in event.lots.all():
        if lot.price > 0:
            has_paid_lots = True
            break

    if has_paid_lots:
        _export_payments(wb.create_sheet(title='Pagamentos'), event)

    wb.save(stream)

    return stream.getvalue()


def _export_subscriptions(worksheet, subscriptions):
    """ Exporta dados de inscrição. """

    worksheet.append([
        'CÓDIGO DA INSCRIÇÃO',
        'LOTE',
        'NOME',
        'DATA NASC',
        'IDADE',
        'EMAIL',
        'PHONE',
        'RUA/LOGRADOURO',
        'COMPLEMENTO',
        'NUMERO',
        'BAIRRO',
        'CEP',
        'CIDADE',
        'UF',
        'INSTITUICAO/EMPRESA',
        'CNPJ',
        'FUNÇÃO/CARGO',
        'CRIADO EM',
    ])

    collector = {}
    for row_idx, sub in enumerate(subscriptions):
        if row_idx == 0:
            continue

        if row_idx not in collector:
            collector[row_idx] = []

        collector[row_idx].append(sub.code)
        collector[row_idx].append(sub.lot.name)
        collector[row_idx].append(sub.person.name)
        collector[row_idx].append(sub.person.age)
        collector[row_idx].append(sub.person.birth_date.strftime('%d/%m/%Y'))
        collector[row_idx].append(sub.person.email)
        collector[row_idx].append(sub.person.phone)
        collector[row_idx].append(sub.person.street)
        collector[row_idx].append(sub.person.complement)
        collector[row_idx].append(sub.person.number)
        collector[row_idx].append(sub.person.village)
        collector[row_idx].append(sub.person.zip_code)
        collector[row_idx].append(sub.person.city.name)
        collector[row_idx].append(sub.person.city.uf)
        collector[row_idx].append(sub.person.institution)
        collector[row_idx].append(sub.person.institution_cnpj)
        collector[row_idx].append(sub.person.function)
        collector[row_idx].append(sub.created.strftime('%d/%m/%Y %H:%M:%S'))

    for row in collector.keys():
        worksheet.append(collector[row])


def _export_payments(worksheet, event):
    worksheet.append([
        'NOME',
        'TIPO',
        'STATUS',
        'DATA PAGAMENTO',
        'VALOR (R$)'
    ])

    statuses = TransactionStatus.objects.filter(
        transaction__subscription__event=event
    )

    collector = {}
    for row_idx, status in enumerate(statuses):
        if row_idx == 0:
            continue

        if row_idx not in collector:
            collector[row_idx] = []

        sub = status.transaction.subscription

        created = datetime.strptime(
            status.date_created,
            "%Y-%m-%dT%H:%M:%S.%fZ"
        )

        collector[row_idx].append(sub.person.name)
        collector[row_idx].append(status.transaction.get_type_display())
        collector[row_idx].append(status.get_status_display())
        collector[row_idx].append(created.strftime(
            '%d/%m/%Y %H:%M:%S'
        ))
        collector[row_idx].append(status.transaction.amount)

    for row in collector.keys():
        worksheet.append(collector[row])
