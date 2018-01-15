""" Formulários de `Person` """
from django import forms

from gatheros_event.models import Person


class PersonForm(forms.ModelForm):
    """ Formulário de Person. """
    class Meta:
        """ Meta """
        model = Person
        fields = '__all__'
