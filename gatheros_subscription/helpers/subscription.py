import locale

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

from openpyxl import Workbook


def export(output_handler, queryset):
    wb = Workbook()

    dados = wb.get_active_sheet()
    dados.title = 'Dados principais'

    def _person(person, field):
        return person._meta.get_field(field).verbose_name

    row = 1
    for instance in queryset:
        # Titulo das colunas
        if row == 1:
            person = instance.person
            dados.cell(column=1, row=row, value=_person(person, 'name'))
            dados.cell(column=2, row=row, value=_person(person, 'gender'))
            dados.cell(column=3, row=row, value=_person(person, 'city'))
            dados.cell(column=4, row=row, value='idade')

        # Valores das colunas
        row += 1
        dados.cell(column=1, row=row, value=instance.person.name)
        dados.cell(column=2, row=row, value=instance.person.gender)
        dados.cell(column=3, row=row, value=str(instance.person.city))
        dados.cell(column=4, row=row, value=instance.person.age)

    wb.save(output_handler)
