""" Formulários de `FormConfig` """
from django import forms

from gatheros_event.helpers.event_business import is_paid_event
from gatheros_subscription.models import FormConfig


class FormConfigForm(forms.ModelForm):
    """ Formulário de Configuração de formulário. """

    class Meta:
        """ Meta """
        model = FormConfig
        fields = [
            'email',
            'cpf',
            'phone',
            'birth_date',
            'address',
            'city',
            'institution',
            'institution_cnpj',
            'function',
        ]

        widgets = {
            'cpf': forms.RadioSelect(),
            'birth_date': forms.RadioSelect(),
            'address': forms.RadioSelect(),
            'institution': forms.RadioSelect(),
            'institution_cnpj': forms.RadioSelect(),
            'function': forms.RadioSelect(),
        }

    def __init__(self, event, **kwargs):
        self.event = event
        self.event_is_payable = is_paid_event(event)

        super().__init__(**kwargs)

        if self.event_is_payable:
            # Força campos como não obrigatórios para não dar erro de submissão
            self.fields['email'].required = False
            self.fields['phone'].required = False
            self.fields['cpf'].required = False
            self.fields['birth_date'].required = False
            self.fields['address'].required = False

    def save(self, commit=True):

        if self.instance and self.event_is_payable:
            # Força valores
            self.instance.email = True
            self.instance.city = True
            self.instance.phone = True

            self.instance.cpf = self.instance.CPF_REQUIRED
            self.instance.birth_date = self.instance.BIRTH_DATE_REQUIRED
            self.instance.address = self.instance.ADDRESS_SHOW

        self.instance.event = self.event

        if self.cleaned_data['address'] == FormConfig.ADDRESS_SHOW:
            self.instance.city = True

        return super().save(commit=commit)
