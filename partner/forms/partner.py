"""
    Partner Form used to validate domain and apply rules
"""
from django import forms
from partner.models import Partner


class PartnerForm(forms.ModelForm):
    """ Partner Form  Implementation"""

    class Meta:
        model = Partner
        fields = ['person']
