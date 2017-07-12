from django import forms

from gatheros_event.models import Place


class PlaceForm(forms.ModelForm):
    """ Formulário de local de evento. """
    class Meta:
        """ Meta """
        model = Place
        fields = '__all__'
        widgets = {'organization': forms.HiddenInput()}
