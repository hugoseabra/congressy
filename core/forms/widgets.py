from datetime import datetime
from django import forms
from django.forms.utils import to_current_timezone
from django.utils.translation import get_language


class AjaxChoiceField(forms.ChoiceField):
    def valid_value(self, value):
        return True


class TelephoneInput(forms.TextInput):
    input_type = 'tel'


class DateInput(forms.DateInput):
    input_type = 'tel'
    template_name = 'forms/widgets/date.html'

    def value_from_datadict(self, data, files, name):
        value = super().value_from_datadict(data, files, name)

        lang = get_language()

        try:
            if lang == 'en' or lang == 'en-us':
                format = '%m/%d/%Y'
            elif lang == 'pt-br':
                format = '%d/%m/%Y'
            else:
                format = '%Y/%m/%d'

            value = datetime.strptime(dt, format)

        except ValueError:
            pass

        return value




class TimeInput(forms.TimeInput):
    input_type = 'tel'
    template_name = 'forms/widgets/time.html'

    def value_from_datadict(self, data, files, name):
        value = super().value_from_datadict(data, files, name)
        if len(value) == 5:
            value += ':00'

        return value

class SplitDateTimeWidget(forms.MultiWidget):
    """
    A Widget that splits datetime input into two <input type="text"> boxes.
    """
    supports_microseconds = False
    template_name = 'forms/widgets/splitdatetime.html'

    def __init__(self, attrs=None, date_format=None, time_format=None):
        now = datetime.now()
        date = DateInput(attrs=attrs, format=date_format)
        time = TimeInput(attrs=attrs, format=time_format)

        super().__init__((date, time), attrs)

    def value_from_datadict(self, data, files, name):
        date, time = super().value_from_datadict(data, files, name)

        if isinstance(date, datetime):
            date = date.strftime('%Y/%m/%d')

        dt = '{} {}'.format(date, time)

        try:
            if lang == 'en' or lang == 'en-us':
                format = '%m/%d/%Y %H:%M:%S'
            elif lang == 'pt-br':
                format = '%d/%m/%Y %H:%M:%S'
            else:
                format = '%Y/%m/%d %H:%M:%S'

            value = datetime.strptime(dt, format)

        except ValueError:
            pass

        return value

    def decompress(self, value):
        if not value:
            return [None, None]

        lang = get_language()
        value = to_current_timezone(value)

        if lang == 'en' or lang == 'en-us':
            date = value.strftime('%m/%d/%Y')
        else:
            date = value.date()

        return [date, value.time().replace(microsecond=0)]

