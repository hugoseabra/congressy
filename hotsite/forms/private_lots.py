"""
    Formulário usado para selecionar o lote do evento.
"""

from datetime import datetime

from django import forms
from django.forms import ModelChoiceField

from gatheros_subscription.models import Lot


class PrivateLotForm(forms.Form):

    def __init__(self, **kwargs):
        self.event = kwargs.get('initial').get('event')
        self.code = kwargs.get('initial').get('code')
        lot = Lot.objects.filter(
            exhibition_code=self.code.upper())
        super().__init__(**kwargs)

        self.fields['lots'] = forms.ModelChoiceField(
            queryset=Lot.objects.filter(event=self.event),
            widget=forms.HiddenInput(),
            initial=lot.first(),
            required=False,
        )
