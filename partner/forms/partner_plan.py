"""
    Partner Plan Form used to validate domain and business rules
"""
from django import forms
from partner.models import PartnerPlan


class PartnerPlanForm(forms.ModelForm):
    """ Partner Plan Form  Implementation"""

    class Meta:
        model = PartnerPlan
        fields = '__all__'
