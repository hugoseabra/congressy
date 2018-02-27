"""
    Partner Contract Form used to validate domain and business rules
"""
from django import forms
from partner.models import PartnerContract


class PartnerContractForm(forms.ModelForm):
    """ Partner Contract Form  Implementation"""

    class Meta:
        model = PartnerContract
        fields = '__all__'
