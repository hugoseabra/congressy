""" Formulários de `Person` """
from django import forms

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
        fields = '__all__'

        widgets = {
            # CPF como telefone para aparecer como número no mobile
            'cpf': TelephoneInput(),
            'phone': TelephoneInput(),
            'birth_date': DateInput(),
            'zip_code': TelephoneInput()
        }
