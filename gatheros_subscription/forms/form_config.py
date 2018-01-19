""" Formulários de `FormConfig` """
from django import forms

from gatheros_subscription.models import FormConfig


class FormConfigForm(forms.ModelForm):
    """ Formulário de Configuração de formulário. """

    class Meta:
        """ Meta """
        model = FormConfig
        fields = [
            'email',
            'phone',
            'city',
            'cpf',
            'birth_date',
            'address',
        ]

        widgets = {
            'cpf': forms.RadioSelect(),
            'birth_date': forms.RadioSelect(),
            'address': forms.RadioSelect(),
        }

    def __init__(self, event, **kwargs):
        self.event = event
        super().__init__(**kwargs)

    def save(self, commit=True):
        self.instance.event = self.event

        if self.cleaned_data['address'] == FormConfig.ADDRESS_SHOW:
            self.instance.city = True

        return super().save(commit=commit)
