from datetime import date

from django import forms
from django.utils.translation import ugettext as _

from gatheros_event.models import Person


class RangeField(forms.MultiValueField):
    default_error_messages = {
        'invalid_start': _(u'Enter a valid start value.'),
        'invalid_end': _(u'Enter a valid end value.'),
    }

    def __init__(self, field_class, widget=forms.NumberInput, *args, **kwargs):
        if 'initial' not in kwargs:
            kwargs['initial'] = ['', '']

        fields = (field_class(), field_class())

        MultiWidget = forms.MultiWidget
        MultiWidget.template_name = 'forms/widgets/multiwidget.html'

        super(RangeField, self).__init__(
            fields=fields,
            widget=MultiWidget(
                widgets=(widget, widget),
                attrs={'min': '1', 'max': 9}),
            *args, **kwargs
        )

    def compress(self, data_list):
        if data_list:
            return [self.fields[0].clean(data_list[0]),
                    self.fields[1].clean(data_list[1])]

        return None


class SubscriptionFilterForm(forms.Form):
    def __init__(self, event, data=None, *args, **kwargs):
        super().__init__(data=data, *args, **kwargs)

