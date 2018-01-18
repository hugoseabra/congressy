""" Formulários de `Person` """
from django.utils import six
from django import forms
from kanu_locations.models import City
from django.db.models.fields import NOT_PROVIDED
from gatheros_event.models import Person


class TelephoneInput(forms.TextInput):
    input_type = 'tel'


class DateInput(forms.TextInput):
    input_type = 'date'


class PersonForm(forms.ModelForm):
    """ Formulário de Person. """

    class Meta:
        """ Meta """
        model = Person
        # fields = '__all__'
        exclude = ('city', 'user',)

        widgets = {
            # CPF como telefone para aparecer como número no mobile
            'cpf': TelephoneInput(),
            'phone': TelephoneInput(),
            'birth_date': DateInput(),
            'zip_code': TelephoneInput()
        }

    def __init__(self, **kwargs):

        # if 'instance' in kwargs:
        #     self.instance = kwargs.get('instance')
        # else:
        #     self.instance = None
        #
        # if 'data' in kwargs:
        #     self.data = kwargs.get('data', {})
        # else:
        #     self.data = {}


        super().__init__(**kwargs)
        self.fill_blank_data_when_user()

    def clean_city(self):
        return City.objects.get(pk=self.data['city'])

    def fill_blank_data_when_user(self):
        """
        When instance has user, the existing data must remain and the blank
        data must be filled.
        """
        if not self.instance:
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
