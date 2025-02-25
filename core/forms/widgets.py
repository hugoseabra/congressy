from datetime import datetime
from decimal import Decimal

from django import forms
from django.forms.utils import to_current_timezone
from django.utils.translation import get_language

from core.forms.cleaners import clear_string


class AjaxChoiceField(forms.ChoiceField):
    def valid_value(self, value):
        return True


class PriceInput(forms.TextInput):
    input_type = 'tel'
    template_name = 'forms/widgets/price.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['lang'] = get_language()
        return context

    def value_from_datadict(self, data, files, name):
        value = super().value_from_datadict(data, files, name)
        if not value:
            value = Decimal(0.00)

        if isinstance(value, Decimal):
            return value

        value = value.replace('.', '').replace(',', '.')
        return round(Decimal(value), 2)


class TelephoneInput(forms.TextInput):
    input_type = 'tel'

    def __init__(self, clear_string=True, attrs=None):
        self.clear_string = clear_string
        super().__init__(attrs)

    def value_from_datadict(self, data, files, name):
        data = super().value_from_datadict(data, files, name)
        if data:
            data = clear_string(str(data)) if self.clear_string else str(data)

        return data


class DateInput(forms.DateInput):
    input_type = 'tel'
    template_name = 'forms/widgets/date.html'

    def value_from_datadict(self, data, files, name):
        value = super().value_from_datadict(data, files, name)

        if not value:
            return value

        if isinstance(value, datetime):
            return value

        lang = get_language()

        try:
            if lang == 'en' or lang == 'en-us':
                # format = '%m/%d/%Y'
                date_format = '%d/%m/%Y'
            elif lang == 'pt-br':
                date_format = '%d/%m/%Y'
            else:
                date_format = '%Y/%m/%d'

            value = datetime.strptime(value, date_format)

        except ValueError:
            pass

        return value


class DateInputBootstrap(forms.DateInput):
    input_type = 'tel'
    template_name = 'forms/widgets/date-bootstrap.html'

    def value_from_datadict(self, data, files, name):
        value = super().value_from_datadict(data, files, name)

        if not value:
            return value

        if isinstance(value, datetime):
            return value

        try:
            date_format = '%d/%m/%Y'

            value = datetime.strptime(value, date_format)

        except ValueError:
            pass

        return value


class TimeInput(forms.TimeInput):
    input_type = 'tel'
    template_name = 'forms/widgets/time.html'

    def value_from_datadict(self, data, files, name):
        value = super().value_from_datadict(data, files, name)

        if not value:
            return value

        if isinstance(value, datetime):
            return value

        if len(value) == 5:
            value += ':00'

        return value


class TimeInputBootstrap(forms.TimeInput):
    input_type = 'tel'
    template_name = 'forms/widgets/time-bootstrap.html'

    def value_from_datadict(self, data, files, name):
        value = super().value_from_datadict(data, files, name)

        if not value:
            return value

        if isinstance(value, datetime):
            return value

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
        date = DateInput(attrs=attrs, format=date_format)
        time = TimeInput(attrs=attrs, format=time_format)

        super().__init__((date, time), attrs)

    def value_from_datadict(self, data, files, name):
        lang = get_language()
        date, time = super().value_from_datadict(data, files, name)

        if isinstance(date, datetime):
            date = date.strftime('%Y-%m-%d')
            date_format = '%Y-%m-%d %H:%M:%S'

        else:
            if lang == 'en' or lang == 'en-us':
                # format = '%m/%d/%Y %H:%M:%S'
                date_format = '%d/%m/%Y %H:%M:%S'
            elif lang == 'pt-br':
                date_format = '%d/%m/%Y %H:%M:%S'
            else:
                date_format = '%Y-%m-%d %H:%M:%S'

        dt = '{} {}'.format(date, time)

        try:
            return datetime.strptime(dt, date_format)

        except ValueError:
            pass

        return [date, time]

    def decompress(self, value):
        if not value:
            return [None, None]

        lang = get_language()
        value = to_current_timezone(value)

        if lang == 'en' or lang == 'en-us':
            # date = value.strftime('%m/%d/%Y')
            date = value.strftime('%d/%m/%Y')
        elif lang == 'pt-br':
            date = value.strftime('%d/%m/%Y')
        else:
            date = value.date()

        return [date, value.time().replace(microsecond=0)]


class SplitDateTimeBootsrapWidget(forms.MultiWidget):
    """
    A Widget that splits datetime input into two <input type="text"> boxes.
    """
    supports_microseconds = False
    template_name = 'forms/widgets/splitdatetime.html'

    def __init__(self, attrs=None, date_format=None, time_format=None):
        date = DateInputBootstrap(attrs=attrs, format=date_format)
        time = TimeInputBootstrap(attrs=attrs, format=time_format)

        super().__init__((date, time), attrs)

    def value_from_datadict(self, data, files, name):
        date, time = super().value_from_datadict(data, files, name)

        if isinstance(date, datetime):
            date = date.strftime('%Y-%m-%d')

        if isinstance(date, datetime):
            time = date.strftime('%H:%M:%S')

        dt = '{} {}'.format(date, time)

        try:
            return datetime.strptime(dt, '%d/%m/%Y %H:%M:%S')

        except ValueError:
            try:
                return datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                pass

        return [date, time]

    def decompress(self, value):
        if not value:
            return [None, None]

        value = to_current_timezone(value)

        date = value.strftime('%d/%m/%Y')

        return [date, value.time().replace(microsecond=0)]


class ColorInput(forms.TextInput):
    input_type = 'color'


class DateTimeInput(forms.DateTimeInput):
    input_type = 'tel'


class ManageableSelect(forms.Select):
    """ Select com ícones de editar e adicionar registros e atualiza-lo. """
    template_name = 'forms/widgets/manageable-select.html'
