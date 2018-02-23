from datetime import date

from django import forms
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _

from gatheros_event.models import Event, Person
from gatheros_subscription.models import Subscription


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
    ufs = forms.MultipleChoiceField(
        label='Estados',
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'checked': 'checked'})
    )

    city = forms.MultipleChoiceField(
        label='Cidades',
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'checked': 'checked'})
    )

    gender = forms.MultipleChoiceField(
        label='Gêneros',
        required=False,
        choices=Person.GENDER_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'checked': 'checked'})
    )

    # noinspection PyTypeChecker
    age = RangeField(
        label='Faixa Etária',
        required=False,
        field_class=forms.IntegerField,
    )

    institutions = forms.MultipleChoiceField(
        label='Instituições',
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'checked': 'checked'})
    )

    def __init__(self, event, data=None, *args, **kwargs):
        super().__init__(data=data, *args, **kwargs)

        subs = event.subscriptions.all()

        # sub_institutions = Subscription.objects \
        #     .filter(event__pk=event.pk) \
        #     .order_by('institution') \
        #     .values_list(
        #         'pk',
        #         'institution',
        #         'person__city__uf',
        #     ).distinct()

        # Estados de acordo com os inscritos do evento
        self.fields['ufs'].choices = self._collect_ufs(subs)
        self.fields['city'].choices = self._collect_cities(subs)
        self.fields['institutions'].choices = self._collect_institutions(subs)

    def _collect_ufs(self, subscriptions):
        return subscriptions \
            .order_by('person__city__uf') \
            .values_list('person__city__uf', 'person__city__uf') \
            .distinct()

    def _collect_cities(self, subscriptions):
        return subscriptions \
            .order_by('person__city__name') \
            .values_list('person__city__id', 'person__city__name') \
            .distinct()

    def _collect_institutions(self, subscriptions):
        return subscriptions \
            .order_by('person__institution') \
            .values_list('person__institution', 'person__institution') \
            .distinct()

    def filter(self, queryset):
        """
        Filtra o queryset pelos campos preenchidos
        :return: queryset
        """
        queryset = self._filter_by_age(queryset)
        queryset = self._filter_by_state(queryset)
        queryset = self._filter_by_gender(queryset)

        return queryset

    def _filter_by_age(self, queryset):
        today = date.today()
        age_start, age_end = (None, None)
        if self.cleaned_data.get('age', ):
            age_start, age_end = self.cleaned_data.get('age')

        if age_end:
            value = date(today.year - (age_end + 1), today.month, today.day)
            queryset = queryset.filter(person__birth_date__gt=value)

        if age_start:
            value = date(today.year - age_start, today.month, today.day)
            queryset = queryset.filter(person__birth_date__lt=value)

        return queryset

    def _filter_by_state(self, queryset):
        if self.cleaned_data['ufs']:
            queryset = queryset.filter(
                person__city__uf__in=self.cleaned_data['ufs']
            )

        return queryset

    def _filter_by_gender(self, queryset):
        if self.cleaned_data['gender']:
            queryset = queryset.filter(
                person__gender__in=self.cleaned_data['gender']
            )

        return queryset
