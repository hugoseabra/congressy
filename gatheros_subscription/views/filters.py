from datetime import date

from django import forms
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _

from gatheros_event.models import Event, Person
from gatheros_subscription.models import Subscription


class RangeWidget(forms.MultiWidget):
    def __init__(self, widget, *args, **kwargs):
        widgets = (widget, widget)

        super(RangeWidget, self).__init__(widgets=widgets, *args, **kwargs)

    def decompress(self, value):
        return value

    def format_output(self, rendered_widgets):
        widget_context = {'min': rendered_widgets[0],
                          'max': rendered_widgets[1], }
        return render_to_string('widgets/range_widget.html', widget_context)


class RangeField(forms.MultiValueField):
    default_error_messages = {
        'invalid_start': _(u'Enter a valid start value.'),
        'invalid_end': _(u'Enter a valid end value.'),
    }

    def __init__(self, field_class, widget=forms.TextInput, *args, **kwargs):
        if not 'initial' in kwargs:
            kwargs['initial'] = ['', '']

        fields = (field_class(), field_class())

        super(RangeField, self).__init__(
            fields=fields,
            widget=RangeWidget(widget),
            *args, **kwargs
        )

    def compress(self, data_list):
        if data_list:
            return [self.fields[0].clean(data_list[0]),
                    self.fields[1].clean(data_list[1])]

        return None


class SubscriptionFilterForm(forms.Form):
    def __init__(self, event, data=None, *args, **kwargs):
        super(SubscriptionFilterForm, self).__init__(data=data, *args,
                                                     **kwargs)
        if isinstance(event, Event):
            event = event.pk

        # Estados de acordo com os inscritos do evento
        self.fields['uf'].choices = Subscription.objects \
            .filter(event__pk=event) \
            .order_by('person__city__uf') \
            .values_list('person__city__uf', 'person__city__uf') \
            .distinct()

    uf = forms.MultipleChoiceField(label='Estado', required=False,
                                   widget=forms.CheckboxSelectMultiple)

    gender = forms.MultipleChoiceField(label='Sexo', required=False,
                                       choices=Person.GENDER_CHOICES,
                                       widget=forms.CheckboxSelectMultiple)

    age = RangeField(label='Faixa Etária', required=False,
                     field_class=forms.IntegerField, widget=forms.NumberInput)

    def filter(self, queryset):
        """
        Filtra o queryset pelos campos preenchidos
        :return: queryset
        """

        # Filtrando por Idade
        today = date.today()
        age_start, age_stop = (None, None)
        if self.cleaned_data.get('age', ):
            age_start, age_stop = self.cleaned_data.get('age')

        if age_stop:
            value = date(today.year - (age_stop + 1), today.month, today.day)
            queryset = queryset.filter(person__birth_date__gt=value)

        if age_start:
            value = date(today.year - age_start, today.month, today.day)
            queryset = queryset.filter(person__birth_date__lt=value)

        # Filtrando por UF
        if self.cleaned_data['uf']:
            queryset = queryset.filter(
                person__city__uf__in=self.cleaned_data['uf'])

        # Filtrando por Sexo
        if self.cleaned_data['gender']:
            queryset = queryset.filter(
                person__gender__in=self.cleaned_data['gender'])

        return queryset
