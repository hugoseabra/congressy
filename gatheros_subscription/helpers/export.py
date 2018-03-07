""" Helper para inscrições. """
import locale
from datetime import datetime

from openpyxl import Workbook
from six import BytesIO

from payment.models import Transaction

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
        if lot.price and lot.price > 0:
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
        'STATUS',
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

    def get_object_value(obj, attr):
        if not hasattr(obj, attr):
            return ''

        return getattr(obj, attr)

    collector = {}
    for row_idx, sub in enumerate(subscriptions):
        if row_idx == 0:
            continue

        if row_idx not in collector:
            collector[row_idx] = []

        person = sub.person
        city = person.city

        collector[row_idx].append(get_object_value(sub, 'code'))
        collector[row_idx].append(get_object_value(sub.lot, 'name'))
        collector[row_idx].append(sub.get_status_display())
        collector[row_idx].append(get_object_value(person, 'name'))

        if person.birth_date:
            collector[row_idx].append(person.age)
            collector[row_idx].append(person.birth_date.strftime('%d/%m/%Y'))
        else:
            collector[row_idx].append('')
            collector[row_idx].append('')

        collector[row_idx].append(get_object_value(person, 'email'))
        collector[row_idx].append(get_object_value(person, 'phone'))
        collector[row_idx].append(get_object_value(person, 'street'))
        collector[row_idx].append(get_object_value(person, 'complement'))
        collector[row_idx].append(get_object_value(person, 'number'))
        collector[row_idx].append(get_object_value(person, 'village'))
        collector[row_idx].append(get_object_value(person, 'zip_code'))
        collector[row_idx].append(get_object_value(city, 'name'))
        collector[row_idx].append(get_object_value(city, 'uf'))
        collector[row_idx].append(get_object_value(person, 'institution'))
        collector[row_idx].append(get_object_value(person, 'institution_cnpj'))
        collector[row_idx].append(get_object_value(person, 'function'))
        collector[row_idx].append(sub.created.strftime('%d/%m/%Y %H:%M:%S'))

    for row in collector.keys():
        worksheet.append(collector[row])


def _export_payments(worksheet, event):
    worksheet.append([
        'NOME',
        'TIPO',
        'STATUS',
        'DATA PAGAMENTO',
        'VALOR INSCRICAO (R$)'
        'VALOR A RECEBER (R$)'
    ])

    transactions = Transaction.objects.filter(subscription__event=event)

    collector = {}
    for row_idx, transaction in enumerate(transactions):
        if row_idx == 0:
            continue

        if row_idx not in collector:
            collector[row_idx] = []

        sub = transaction.subscription

        created = datetime.strptime(
            transaction.date_created,
            "%Y-%m-%dT%H:%M:%S.%fZ"
        )

        collector[row_idx].append(sub.person.name)
        collector[row_idx].append(transaction.get_type_display())
        collector[row_idx].append(transaction.get_status_display())
        collector[row_idx].append(created.strftime('%d/%m/%Y %H:%M:%S'))
        collector[row_idx].append(transaction.amount)
        collector[row_idx].append(transaction.liquid_amount)

    for row in collector.keys():
        worksheet.append(collector[row])
