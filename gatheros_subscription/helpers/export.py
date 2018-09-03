""" Helper para inscrições. """
import locale

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
        ':',
        '?',
    )
    for char in invalid_chars:
        title = title.replace(char, '_')

    return title[0:28]


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

    _export_subscriptions(ws1, event.subscriptions.filter(completed=True,
                                                          test_subscription=False))

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

    for lot_category in event.lot_categories.all():
        cat_name = lot_category.name

        products_queryset = lot_category.product_optionals
        services_queryset = lot_category.service_optionals

        if products_queryset.count():
            num_subs = products_queryset.filter(
                subscription_products__subscription__completed=True,
                subscription_products__subscription__test_subscription=False
            ).count()

            if num_subs > 0:
                sheet_name = 'Opcionais - {}'.format(cat_name)
                title = clean_sheet_title(sheet_name)
                worksheet = wb.create_sheet(title=title)

                _export_addon_products(
                    worksheet,
                    sheet_name,
                    products_queryset.all()
                )

        if services_queryset.count():
            num_subs = services_queryset.filter(
                subscription_services__subscription__completed=True,
                subscription_services__subscription__test_subscription=False
            ).count()

            if num_subs > 0:
                sheet_name = 'Ativ. Extras - {}'.format(cat_name)
                title = clean_sheet_title(sheet_name)
                worksheet = wb.create_sheet(title=title)

                _export_addon_services(
                    worksheet,
                    sheet_name,
                    services_queryset.all()
                )

    wb.save(stream)

    return stream.getvalue()


def _export_subscriptions(worksheet, subscriptions):
    """ Exporta dados de inscrição. """

    worksheet.append([
        'NÚMERO DE INSCRIÇÃO',
        'CÓDIGO DA INSCRIÇÃO',
        'CATEGORIA DE PARTICIPANTE',
        'LOTE',
        'STATUS',
        'SEXO',
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

        collector[row_idx].append(get_object_value(sub, 'event_count'))
        collector[row_idx].append(get_object_value(sub, 'code'))
        try:
            collector[row_idx].append(sub.lot.category.name)
        except AttributeError:
            collector[row_idx].append('')

        collector[row_idx].append(get_object_value(sub.lot, 'name'))

        collector[row_idx].append(sub.get_status_display())
        collector[row_idx].append(person.get_gender_display())

        collector[row_idx].append('Sim' if sub.attended else 'Não')
        collector[row_idx].append(
            sub.attended_on.strftime('%d/%m/%Y') if sub.attended else ''
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
        'NÚMERO DE INSCRIÇÃO',
        'CÓDIGO DA INSCRIÇÃO',
        'NOME',
        'TIPO',
        'STATUS',
        'DATA PAGAMENTO',
        'VALOR INSCRICAO (R$)',
        'VALOR A RECEBER (R$)',
    ])

    transactions = Transaction.objects.filter(subscription__event=event)

    collector = {}
    row_idx = 1
    for transaction in transactions:
        if row_idx not in collector:
            collector[row_idx] = []

        sub = transaction.subscription

        created = transaction.date_created.strftime('%d/%m/%Y %H:%M:%S')

        collector[row_idx].append(get_object_value(sub, 'event_count'))
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
        'NÚMERO DE INSCRIÇÃO',
        'CÓDIGO DA INSCRIÇÃO',
        'NOME',
        'E-MAIL',
    ]

    survey = event_survey.survey

    questions = survey.questions.all().order_by('order')

    # Lista a ser consultada para pegar a sequência de colunas de perguntas.
    question_pks = []
    for question in questions:
        # Adiciona coluna da pergunta
        column_name = str(question.label).upper()

        if question.required is True:
            column_name = '* {}'.format(column_name)

        if question.active is False:
            column_name += ' (desativado)'

        columns.append(column_name)

        # Marca coluna da pergunta pelo índice da lista
        question_pks.append(question.pk)

    worksheet.append(columns)

    event = event_survey.event
    subscriptions = event.subscriptions.filter(completed=True,
                                               test_subscription=False,
                                               author__isnull=False)

    collector = {}
    row_idx = 1
    for sub in subscriptions:
        person = sub.person

        if row_idx not in collector:
            collector[row_idx] = []

        answers = Answer.objects.filter(
            question__survey=survey,
            author=sub.author,
        ).order_by('question__order')

        if not answers:
            continue

        answers_values = {}
        for answer in answers:
            answers_values[answer.question.pk] = answer.human_display

        collector[row_idx].append(get_object_value(sub, 'event_count'))
        collector[row_idx].append(get_object_value(sub, 'code'))
        collector[row_idx].append(person.name)
        collector[row_idx].append(person.email)

        # Varrer por pergunta para depois encontrar as respostas.
        for question in questions:
            # Se não há resposta, deixar em branco.
            collector[row_idx].append(answers_values.get(question.pk, '-'))

        row_idx += 1

    for row in collector.keys():
        worksheet.append(collector[row])


def _export_addon_products(worksheet, title, products):
    """
    Exporta Insrições de Opcionais de um evento.
    """
    columns = [
        'CATEGORIA',
        'NÚMERO DE INSCRIÇÃO',
        'CÓDIGO DA INSCRIÇÃO',
        'NOME',
        'E-MAIL',
        'NOME DO OPCIONAL',
        'STATUS',
        'DATA PAGAMENTO',
        'VALOR INSCRICAO (R$)',
        'VALOR A RECEBER (R$)',
    ]

    collector = {}
    row_idx = 1

    for product in products:
        subs = product.subscription_products.filter(
            subscription__completed=True,
            subscription__test_subscription=False,
        )

        for addon_sub in subs:
            sub = addon_sub.subscription
            person = sub.person

            created = addon_sub.created.strftime('%d/%m/%Y %H:%M:%S')

            if row_idx not in collector:
                collector[row_idx] = []

            collector[row_idx].append(sub.lot.category.name)
            collector[row_idx].append(get_object_value(sub, 'event_count'))
            collector[row_idx].append(get_object_value(sub, 'code'))
            collector[row_idx].append(person.name)
            collector[row_idx].append(person.email)
            collector[row_idx].append(addon_sub.optional.name)
            collector[row_idx].append(sub.get_status_display())
            collector[row_idx].append(created)
            collector[row_idx].append(addon_sub.optional_price)
            collector[row_idx].append(addon_sub.optional_liquid_price)

            row_idx += 1

    rows = collector.keys()

    if rows:
        worksheet.append(columns)
        [worksheet.append(collector[row]) for row in rows]


def _export_addon_services(worksheet, title, services):
    """
    Exporta Insrições de atividades extras.
    """
    columns = [
        'CATEGORIA',
        'NÚMERO DE INSCRIÇÃO',
        'CÓDIGO DA INSCRIÇÃO',
        'NOME',
        'E-MAIL',
        'TEMA',
        'NOME DA ATIVIDADE EXTRA',
        'STATUS',
        'DATA PAGAMENTO',
        'VALOR INSCRICAO (R$)',
        'VALOR A RECEBER (R$)',
    ]

    collector = {}
    row_idx = 1

    for service in services:
        subs = service.subscription_services.filter(
            subscription__completed=True,
            subscription__test_subscription=False,
        )

        for addon_sub in subs:
            sub = addon_sub.subscription
            person = sub.person

            created = addon_sub.created.strftime('%d/%m/%Y %H:%M:%S')

            if row_idx not in collector:
                collector[row_idx] = []

            collector[row_idx].append(sub.lot.category.name)
            collector[row_idx].append(get_object_value(sub, 'event_count'))
            collector[row_idx].append(get_object_value(sub, 'code'))
            collector[row_idx].append(person.name)
            collector[row_idx].append(person.email)
            collector[row_idx].append(addon_sub.optional.theme.name)
            collector[row_idx].append(addon_sub.optional.name)
            collector[row_idx].append(sub.get_status_display())
            collector[row_idx].append(created)
            collector[row_idx].append(addon_sub.optional_price)
            collector[row_idx].append(addon_sub.optional_liquid_price)

            row_idx += 1

    rows = collector.keys()

    if rows:
        worksheet.append(columns)
        [worksheet.append(collector[row]) for row in rows]
