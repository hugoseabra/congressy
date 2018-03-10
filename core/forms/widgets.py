from datetime import datetime
from django import forms
from django.forms.utils import to_current_timezone


class AjaxChoiceField(forms.ChoiceField):
    def valid_value(self, value):
        return True


class TelephoneInput(forms.TextInput):
    input_type = 'tel'


class DateInput(forms.DateInput):
    input_type = 'tel'
    template_name = 'forms/widgets/date.html'


class TimeInput(forms.TimeInput):
    input_type = 'tel'
    template_name = 'forms/widgets/time.html'


class SplitDateTimeWidget(forms.MultiWidget):
    """
    A Widget that splits datetime input into two <input type="text"> boxes.
    """
    supports_microseconds = False
    template_name = 'forms/widgets/splitdatetime.html'

    def __init__(self, attrs=None, date_format=None, time_format=None):

        now = datetime.now()

        date_attrs = attrs or {}
        date_attrs.update({
            'placeholder': now.strftime('%d/%m/%Y')
        });
        date = DateInput(attrs=date_attrs, format=date_format)

        time_attrs = attrs or {}
        time_attrs.update({
            'placeholder': now.strftime('%H:%M')
        });
        time = TimeInput(attrs=time_attrs, format=time_format)

        super().__init__((date, time), attrs)

    def value_from_datadict(self, data, files, name):
        value = super().value_from_datadict(data, files, name)
        if len(value) == 2:
            if len(value[1]) == 5:
                value[1] += ':00'

            dt = '{} {}'.format(value[0], value[1])

            try:
                value = datetime.strptime(dt, '%d/%m/%Y %H:%M:%S')
            except ValueError:
                # message handled by field
                forms.ValidationError('')

        return value

    def decompress(self, value):
        if value:
            value = to_current_timezone(value)
            return [value.date(), value.time().replace(microsecond=0)]
        return [None, None]
