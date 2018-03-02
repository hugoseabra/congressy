""" Formulários de `Person` """
from django import forms
from django.db.models.fields import NOT_PROVIDED
from django.utils import six
from django.utils.datastructures import MultiValueDictKeyError
from kanu_locations.models import City

from core.forms.widgets import DateInput, AjaxChoiceField, TelephoneInput
from gatheros_event.models import Occupation, Person


def create_years_list():
    years = []
    epoch = 1950
    for i in range(60):
        epoch += 1
        years.append(epoch)

    return years


class PersonForm(forms.ModelForm):
    """ Formulário de Person. """

    states = (
        ('', '----'),
        # replace the value '----' with whatever you want, it won't matter
        ("AC", "Acre"),
        ("AL", "Alagoas"),
        ("AP", "Amapá"),
        ("AM", "Manaus"),
        ("BA", "Bahia"),
        ("CE", "Ceará"),
        ("DF", "Distrito Federal"),
        ("ES", "Espírito Santo"),
        ("GO", "Goiás"),
        ("MA", "Maranhão"),
        ("MT", "Mato Grosso"),
        ("MS", "Mato Grosso do Sul"),
        ("MG", "Minas Gerais"),
        ("PA", "Pará"),
        ("PB", "Paraíba"),
        ("PR", "Paraná"),
        ("PE", "Pernambuco"),
        ("PI", "Piauí"),
        ("RJ", "Rio de Janeiro"),
        ("RN", "Rio Grande do Norte"),
        ("RS", "Rio Grande do Sul"),
        ("RO", "Rondônia"),
        ("RR", "Roraima"),
        ("SC", "Santa Catarina"),
        ("SP", "São Paulo"),
        ("SE", "Sergipe"),
        ("TO", "Tocantins"),
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
        exclude = ('user', 'occupation')

        widgets = {
            # CPF como telefone para aparecer como número no mobile
            'cpf': TelephoneInput(),
            'name': forms.TextInput(attrs={'placeholder': 'Nome completo'}),
            'email': forms.EmailInput(attrs={'placeholder': 'me@you.com'}),
            'phone': TelephoneInput(attrs={'placeholder': '(00) 00000-0000'}),
            'zip_code': TelephoneInput(),
            'city': forms.HiddenInput(),
            'birth_date': forms.SelectDateWidget(
                attrs=({'style': 'width: 30%; display: inline-block;'}),
                years=create_years_list(), )
        }

    def __init__(self, is_chrome=False, **kwargs):

        uf = None
        if 'instance' in kwargs:
            instance = kwargs.get('instance')
            if instance.city:
                uf = instance.city.uf

        if 'initial' in kwargs and uf:
            initial = kwargs.get('initial')
            initial.update({'state': uf})
            kwargs.update({'initial': initial})

        super().__init__(**kwargs)

        if is_chrome:
            self.fields['birth_date'].widget = DateInput()


    def setAsRequired(self, field_name):
        if field_name not in self.fields:
            return

        self.fields[field_name].required = True

    def clean_cpf(self):
        return self.clear_string(self.data.get('cpf'))

    def clean_zip_code(self):
        return self.clear_string(self.data.get('zip_code'))

    def clean_phone(self):
        return self.clear_string(self.data.get('phone'))

    def clean_institution_cnpj(self):
        return self.clear_string(self.data.get('institution_cnpj'))

    def clean_city(self):
        if 'city' not in self.data:
            return None

        return City.objects.get(pk=self.data['city'])

    def clean_email(self):
        try:
            email = self.data['email']
        except MultiValueDictKeyError:
            email = self.initial['email']
        return email.lower()

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

    @staticmethod
    def clear_string(string):
        if not string:
            return ''

        return str(string) \
            .replace('.', '') \
            .replace('-', '') \
            .replace('/', '') \
            .replace('(', '') \
            .replace(')', '') \
            .replace(' ', '')
