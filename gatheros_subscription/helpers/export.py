""" Helper para inscrições. """
import locale
from datetime import datetime

from openpyxl import Workbook
from six import BytesIO

from payment.models import Transaction
from survey.models import Answer

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')


def get_object_value(obj, attr):
    if not hasattr(obj, attr):
        return ''

    return getattr(obj, attr)


def clean_sheet_title(title):
    """ Limpa título de guia da planilha. """
    title = str(title)

    invalid_chars = (
        '!',
        '@',
        '#',
        '/',
        '&',
        '*',
    )
    for char in invalid_chars:
        title = title.replace(char, '_')

    return title[0:30]


def export_event_data(event):
    """
    Exportação do queryset de inscrições em formato xlsx

    :param event:
    :return: ByteIO
    """
    stream = BytesIO()

    wb = Workbook()

    ws1 = wb.active
    ws1.title = clean_sheet_title('Participantes')

    _export_subscriptions(ws1, event.subscriptions.filter(completed=True))

    has_paid_lots = False
    for lot in event.lots.all():
        if lot.price and lot.price > 0:
            has_paid_lots = True
            break

    if has_paid_lots:
        _export_payments(wb.create_sheet(title='Pagamentos'), event)

    for ev_survey in event.surveys.all():
        title = clean_sheet_title(
            'Formulário-{}'.format(ev_survey.survey.name)
        )
        _export_survey_answers(wb.create_sheet(title=title), ev_survey)

    wb.save(stream)

    return stream.getvalue()


def _export_subscriptions(worksheet, subscriptions):
    """ Exporta dados de inscrição. """

    worksheet.append([
        'CÓDIGO DA INSCRIÇÃO',
        'CATEGORIA DE PARTICIPANTE',
        'LOTE',
        'STATUS',
        'CREDENCIADO (CHECK-IN)',
        'CREDENCIADO EM',
        'NOME',
        'CPF',
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
    row_idx = 1
    for sub in subscriptions:
        if row_idx not in collector:
            collector[row_idx] = []

        person = sub.person
        city = person.city

        collector[row_idx].append(get_object_value(sub, 'code'))
        try:
            collector[row_idx].append(sub.lot.category.name)
        except AttributeError:
            collector[row_idx].append('')

        collector[row_idx].append(get_object_value(sub.lot, 'name'))

        collector[row_idx].append(sub.get_status_display())

        collector[row_idx].append('Sim' if sub.attended else 'Não')
        collector[row_idx].append(
            sub.attended.strftime('%d/%m/%Y') if sub.attended else ''
        )

        collector[row_idx].append(get_object_value(person, 'name'))
        collector[row_idx].append(get_object_value(person, 'cpf'))

        if person.birth_date:
            collector[row_idx].append(person.birth_date.strftime('%d/%m/%Y'))
            collector[row_idx].append(person.age)
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

        row_idx += 1

    for row in collector.keys():
        worksheet.append(collector[row])


def _export_payments(worksheet, event):
    worksheet.append([
        'CÓDIGO',
        'NOME',
        'TIPO',
        'STATUS',
        'DATA PAGAMENTO',
        'VALOR INSCRICAO (R$)'
        'VALOR A RECEBER (R$)'
    ])

    transactions = Transaction.objects.filter(subscription__event=event)

    collector = {}
    row_idx = 1
    for transaction in transactions:
        if row_idx not in collector:
            collector[row_idx] = []

        sub = transaction.subscription

        created = transaction.date_created.strftime('%d/%m/%Y %H:%M:%S')

        collector[row_idx].append(get_object_value(sub, 'code'))
        collector[row_idx].append(sub.person.name)
        collector[row_idx].append(transaction.get_type_display())
        collector[row_idx].append(transaction.get_status_display())
        collector[row_idx].append(created)
        collector[row_idx].append(transaction.amount)
        collector[row_idx].append(transaction.liquid_amount)

        row_idx += 1

    for row in collector.keys():
        worksheet.append(collector[row])


def _export_survey_answers(worksheet, event_survey):
    """
    Exporta as respostas de survey.
    """

    columns = [
        'CÓDIGO',
        'NOME',
        'E-MAIL',
    ]

    survey = event_survey.survey
    subscriptions = event_survey.event.subscriptions.filter(completed=True)
    questions = survey.questions.all().order_by('order')

    # Lista a ser consultada para pegar a sequência de colunas de perguntas.
    question_pks = []
    for question in questions:
        # Adiciona coluna da pergunta
        columns.append(str(question.label).upper())

        # Marca coluna da pergunta pelo índice da lista
        question_pks.append(question.pk)

    worksheet.append(columns)

    collector = {}
    row_idx = 1
    for sub in subscriptions:
        person = sub.person

        if row_idx not in collector:
            collector[row_idx] = []

        answers = Answer.objects.filter(
            question__survey=survey,
            author__user=person.user,
        ).order_by('question__order')

        if not answers:
            continue

        collector[row_idx].append(get_object_value(sub, 'code'))
        collector[row_idx].append(person.name)
        collector[row_idx].append(person.email)

        for answer in answers:
            question = answer.question

            # Varrer até achar a coluna da pergunta
            for question_pk in question_pks:
                if question_pk == question.pk:
                    # Se não há resposta, deixar em branco.
                    collector[row_idx].append(answer.human_display)

        row_idx += 1

    for row in collector.keys():
        worksheet.append(collector[row])
