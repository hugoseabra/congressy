from django import forms
from django.utils.translation import gettext as _

from base import managers
from payment.models import Benefactor


class BenefactorManager(managers.Manager):
    """ Manager de Benefactor. """

    required_for_national = [
        'street',
        'number',
        'village',
        'city',
        'zip_code',
    ]

    required_for_international = [
        'address_international',
        'city_international',
        'state_international',
        'zip_code_international',
    ]

    required_for_legal = [
        'cnpj',
    ]

    required_for_legal_international = [
        'ein',
    ]

    required_for_person = [
        'gender',
        'birth_date',
        'cpf',
    ]

    required_for_person_international = [
        'gender',
        'birth_date',
        'doc_type',
        'doc_number',
    ]

    class Meta:
        model = Benefactor
        fields = '__all__'

    def clean_number(self):
        number = self.cleaned_data.get('number', '')
        if not number:
            number = ''

        return number

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')

        if cpf:
            cpf = str(cpf).zfill(11)

        return cpf

    def clean_cnpj(self):
        cnpj = self.cleaned_data.get('cnpj')

        if cnpj:
            cnpj = str(cnpj).zfill(14)

        return cnpj

    def clean_beneficiary(self):
        beneficiary_id = self.cleaned_data.get('beneficiary')

        if self.instance.pk and self.instance.beneficiary_id != beneficiary_id:
            raise forms.ValidationError('Você não pode editar benfeitor.')

        return beneficiary_id

    def clean(self):
        clean_data = super().clean()
        msg = "Este campo é obrigatório."

        if clean_data.get('is_company'):
            if clean_data.get('country') and \
                    clean_data.get('country').lower() != "br":
                type_required = self.required_for_legal_international
            else:
                type_required = self.required_for_legal

        else:
            if clean_data.get('country') and \
                    clean_data.get('country').lower() != "br":
                type_required = self.required_for_person_international
            else:
                type_required = self.required_for_person

        if clean_data.get('country') and \
                clean_data.get('country').lower() != "br":
            country_required = self.required_for_international
        else:
            country_required = self.required_for_national

        required_fields = type_required + country_required

        error_list = dict()

        for field in required_fields:
            if clean_data[field] is None:
                error_list.update({field: _(msg)})

        if error_list:
            raise forms.ValidationError(error_list)

        return clean_data
