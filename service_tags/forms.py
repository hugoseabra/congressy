from django import forms

from service_tags.models import CustomServiceTag


class CustomServiceTagForm(forms.ModelForm):
    class Meta:
        model = CustomServiceTag
        fields = '__all__'
