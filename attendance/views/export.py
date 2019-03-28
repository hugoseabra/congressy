import locale
from datetime import datetime
from django.http import HttpResponse
from django.views.generic import View
from openpyxl import Workbook
from six import BytesIO

from attendance.helpers.attendance import subscription_is_checked
from attendance.models import AttendanceService, Checkin
from gatheros_subscription.helpers.export import clean_sheet_title, \
    get_object_value
from .mixins import AttendancesFeatureFlagMixin

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')


class AttendanceXLSExportView(AttendancesFeatureFlagMixin, View):

    # @TODO Implement security features.
    #  For now any authenticated user can access this.

    def get(self, request, *args, **kwargs):
        # Chamando exportação
        output = export_attendance(515)

        # Criando resposta http com arquivo de download
        response = HttpResponse(
            output,
            content_type="application/vnd.ms-excel"
        )

        # Definindo nome do arquivo
        name = "%s_%s.xlsx" % (
            self.event.slug,
            datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        )
        response['Content-Disposition'] = 'attachment; filename=%s' % name

        return response


def export_attendance(attendance_service_pk: int):
    """
    Exportação de inscrições de um serviço de atendimento em formato xlsx

    :return: ByteIO
    """
    stream = BytesIO()

    wb = Workbook()

    ws1 = wb.active
    ws1.title = clean_sheet_title('Participantes')
    wb.create_sheet(title='Detalhamento')

    try:
        service = AttendanceService.objects.get(pk=attendance_service_pk)
    except AttendanceService.DoesNotExist:
        ws1.append(["ERRO: Não foi possivel encontrar esse serviço de "
                    "atendimento."])
        wb.save(stream)
        return stream.getvalue()

    checkins = Checkin.objects.filter(
        attendance_service=service,
        checkout__isnull=True,
    )

    subscriptions = list()

    for checkin in checkins:
        subscriptions.append(checkin.subscription)

    if len(subscriptions) == 0:
        ws1.append(["Nenhuma inscrição neste serviço de atendimento"])
    else:
        export_attendance_checkin_subscriptions(ws1, subscriptions, service)

    wb.save(stream)
    return stream.getvalue()


def export_attendance_checkin_subscriptions(worksheet, subscriptions,
                                            attendance):
    """ Exporta dados de inscrição. """

    worksheet.append([
        'NÚMERO DE INSCRIÇÃO',
        'CÓDIGO DA INSCRIÇÃO',
        'CATEGORIA DE PARTICIPANTE',
        'LOTE',
        'STATUS',
        'ATENDIDO',
        'SEXO',
        'NOME',
        'TIPO DE DOCUMENTO',
        'NÚMERO DO DOCUMENTO',
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
        'PAÍS',
        'INSTITUICAO/EMPRESA',
        'CNPJ',
        'FUNÇÃO/CARGO',
        'TAG DE AGRUPAMENTO',
        'INFO. PARA CRACHÁ',
        'OBS',
        'CRIADO EM',
        'HORA REGISTRADA',
    ])

    collector = {}
    row_idx = 1
    for sub in subscriptions:

        checkin = Checkin.objects.get(
            subscription=sub,
            checkout__isnull=True,
            attendance_service=attendance,
        )

        if row_idx not in collector:
            collector[row_idx] = []

        person = get_object_value(
            obj=sub,
            attr='person',
            cached_type='subscriptions',
        )

        lot = get_object_value(
            obj=sub,
            attr='lot',
            cached_type='subscriptions',
        )

        lot_category = get_object_value(
            obj=lot,
            attr='category',
            cached_type='lots',
        )

        city = get_object_value(
            obj=person,
            attr='city',
            cached_type='people',
        )

        collector[row_idx].append(get_object_value(
            obj=sub,
            attr='event_count',
            cached_type='subscriptions',
        ))

        collector[row_idx].append(get_object_value(
            obj=sub,
            attr='code',
            cached_type='subscriptions',
        ))

        collector[row_idx].append(lot_category.name)

        collector[row_idx].append(lot.name)

        collector[row_idx].append(sub.get_status_display())

        if subscription_is_checked(sub.pk):
            is_checked = "Sim"
        else:
            is_checked = "Não"

        collector[row_idx].append(is_checked)
        collector[row_idx].append(person.get_gender_display())

        collector[row_idx].append(get_object_value(person, 'name'))

        country = get_object_value(person, 'country')
        if country == 'BR':
            doc_type = 'CPF'
            doc_num = get_object_value(person, 'cpf')
        else:
            doc_type = get_object_value(person, 'international_doc_type')
            doc_num = get_object_value(person, 'international_doc')

        collector[row_idx].append(doc_type)
        collector[row_idx].append(doc_num)

        if person.birth_date:
            collector[row_idx].append(person.birth_date.strftime('%d/%m/%Y'))
            collector[row_idx].append(person.age)
        else:
            collector[row_idx].append('')
            collector[row_idx].append('')

        collector[row_idx].append(get_object_value(person, 'email'))
        collector[row_idx].append(get_object_value(person, 'phone'))
        if country == 'BR':
            street = get_object_value(person, 'street')
            number = get_object_value(person, 'number')
            village = get_object_value(person, 'village')
            zip_code = get_object_value(person, 'zip_code')
            city_name = get_object_value(city, 'name')
            uf = get_object_value(city, 'uf')

        else:
            street = get_object_value(person, 'address_international')
            number = ''
            village = ''
            zip_code = get_object_value(person, 'zip_code_international')
            city_name = get_object_value(person, 'city_international')
            uf = get_object_value(person, 'state_international')

        collector[row_idx].append(street)
        collector[row_idx].append(get_object_value(person, 'complement'))
        collector[row_idx].append(number)
        collector[row_idx].append(village)
        collector[row_idx].append(zip_code)
        collector[row_idx].append(city_name)
        collector[row_idx].append(uf)
        collector[row_idx].append(country)
        collector[row_idx].append(get_object_value(person, 'institution'))
        collector[row_idx].append(get_object_value(person, 'institution_cnpj'))
        collector[row_idx].append(get_object_value(person, 'function'))
        collector[row_idx].append(get_object_value(sub, 'tag_group'))
        collector[row_idx].append(get_object_value(sub, 'tag_info'))
        collector[row_idx].append(get_object_value(sub, 'obs'))
        collector[row_idx].append(sub.created.strftime('%d/%m/%Y %H:%M:%S'))
        if checkin.registration:
            collector[row_idx].append(
                checkin.registration.strftime('%d/%m/%Y %H:%M:%S'))
        else:
            '----'

        row_idx += 1

    for row in collector.keys():
        worksheet.append(collector[row])
