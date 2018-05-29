"""Formulários do módulo de certificados. """
from django import forms

from certificate.models import Certificate


class CertificateForm(forms.ModelForm):
    """ Formulário de lote. """

    class Meta:
        """ Meta """
        model = Certificate
        fields = '__all__'
