""" Formulários de `Person` """
from django import forms
from django.db.models.fields import NOT_PROVIDED
from django.utils import six
from localflavor.br.forms import BRCPFField, BRCNPJField

from core.forms.cleaners import clear_string, clean_cellphone as phone_cleaner
from core.forms.widgets import (
    AjaxChoiceField,
    DateInput,
    TelephoneInput,
)
from core.util import create_years_list
from gatheros_event.models import Occupation, Person


# class InternationalTelephoneInput(forms.MultiWidget):
#     template_name = 'forms/widgets/international_phone.html'
#
#     def __init__(self, attrs=None):
#         if attrs is not None and isinstance(attrs, dict):
#             ddi_attrs = attrs.get('ddi')
#             phone_attrs = attrs.get('phone')
#             country_attrs = attrs.get('country')
#         else:
#             ddi_attrs = None
#             phone_attrs = None
#             country_attrs = None
#
#         ddi = forms.TextInput(attrs=ddi_attrs)
#         phone = TelephoneInput(attrs=phone_attrs)
#         country = forms.TextInput(attrs=country_attrs)
#
#         super().__init__((ddi, phone, country), attrs)
#
#     def decompress(self, value):
#         if not value:
#             return [None, None, None]
#
#         return [value, value, value]


class PersonForm(forms.ModelForm):
    """ Formulário de Person. """

    states = (
        ('', '----'),
        # replace the value '----' with whatever you want, it won't matter
        ("AC", "AC"),
        ("AL", "AL"),
        ("AP", "AP"),
        ("AM", "AM"),
        ("BA", "BA"),
        ("CE", "CE"),
        ("DF", "DF"),
        ("ES", "ES"),
        ("GO", "GO"),
        ("MA", "MA"),
        ("MT", "MT"),
        ("MS", "MS"),
        ("MG", "MG"),
        ("PA", "PA"),
        ("PB", "PB"),
        ("PR", "PR"),
        ("PE", "PE"),
        ("PI", "PI"),
        ("RJ", "RJ"),
        ("RN", "RN"),
        ("RS", "RS"),
        ("RO", "RO"),
        ("RR", "RR"),
        ("SC", "SC"),
        ("SP", "SP"),
        ("SE", "SE"),
        ("TO", "TO"),
    )
    empty = (
        ('', '----'),
    )

    state = forms.ChoiceField(label='Estado', choices=states, required=False)
    city_name = AjaxChoiceField(label='Cidade', choices=empty, required=False)

    class Meta:
        """ Meta """
        model = Person
        # fields = '__all__'
        exclude = (
            'user',
            'occupation',
            'skype',
            'linkedin',
            'twitter',
            'facebook',
            'website',
            'avatar',
            'synchronized',
            'rg',
            'orgao_expedidor',
            'pne',
            'politics_version',
            'term_version',
        )

        widgets = {
            # CPF como telefone para aparecer como número no mobile
            'cpf': TelephoneInput,
            'name': forms.TextInput(attrs={'placeholder': 'Nome completo'}),
            'email': forms.EmailInput(attrs={
                'placeholder': 'me@you.com',
                'style': 'text-transform:lowercase'
            }),
            'phone': TelephoneInput,
            'zip_code': TelephoneInput,
            'city': forms.HiddenInput(),
            'birth_date': forms.SelectDateWidget(
                attrs=({'style': 'width: 30%; display: inline-block;'}),
                years=create_years_list(),
            )
        }

    def __init__(self, is_chrome=False, **kwargs):

        uf = None

        instance = kwargs.get('instance')
        initial = kwargs.get('initial')

        if not initial:
            initial = {}

        if instance:
            if instance.city:
                uf = instance.city.uf

        if uf:
            initial.update({'state': uf})
            kwargs.update({'initial': initial})

        super().__init__(**kwargs)

        if is_chrome:
            self.fields['birth_date'].widget = DateInput()

    def setAsRequired(self, field_name):
        if field_name not in self.fields:
            return

        self.fields[field_name].required = True

    def clean_zip_code(self):
        zip_code = self.cleaned_data.get('zip_code')

        if zip_code:
            zip_code = clear_string(zip_code)
            if len(zip_code) != 8:
                raise forms.ValidationError(
                    'O CEP deve não está correto. Verifique a quantidade de'
                    ' caracteres.'
                )

        return zip_code

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if cpf:
            cpf = BRCPFField().clean(cpf)
            return clear_string(cpf)
        return cpf

    def clean_institution_cnpj(self):
        cnpj = self.cleaned_data.get('institution_cnpj')

        if cnpj:
            cnpj = BRCNPJField().clean(cnpj)
            return clear_string(cnpj)

        return cnpj

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            phone = phone_cleaner(phone)
        return phone

    def clean_email(self):
        email = self.cleaned_data['email']

        if email:
            return email.lower()

        return email

    def clean_occupation(self):
        return Occupation.objects.get(pk=self.data['occupation'])

    def fill_blank_data_when_user(self):
        """
        When instance has user, the existing data must remain and the blank
        data must be filled.
        """
        if not self.instance:
            return

        if self.instance.user is None:
            return

        fields = [field for field in six.iterkeys(self.data)]

        for field_name in fields:
            incoming_value = self.data.get(field_name)

            # If incoming value is not blank
            if not incoming_value:
                continue

            # If field_name does exist in instance
            if not hasattr(self.instance, field_name):
                continue

            field = self.instance._meta.get_field(field_name)
            has_default = field.default != NOT_PROVIDED
            value = getattr(self.instance, field_name)

            # If value exists and it does not come from a default value
            if not value or (value and has_default):
                continue

            # Remain same value from persistence
            self.data[field_name] = value
