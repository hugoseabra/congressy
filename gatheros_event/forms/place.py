from django import forms

from gatheros_event.models import Place


class PlaceForm(forms.ModelForm):
    class Meta:
        model = Place
        fields = '__all__'
        widgets = {'organization': forms.HiddenInput()}
