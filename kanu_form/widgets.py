from django.forms import fields


class DateInput(fields.DateInput):
    input_type = 'date'
    template_name = 'kanu_form/date_input.html'


class DateTimeInput(fields.DateTimeInput):
    input_type = 'date'
    template_name = 'kanu_form/datetime_input.html'


class EmailInput(fields.EmailInput):
    template_name = 'kanu_form/email_input.html'


class TelInput(fields.TextInput):
    template_name = 'kanu_form/tel_input.html'
