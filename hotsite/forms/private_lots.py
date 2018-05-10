"""
    Formulário usado para selecionar o lote do evento.
"""

from django import forms

from gatheros_subscription.models import Lot


class PrivateLotForm(forms.Form):

    def __init__(self, event, code, **kwargs):
        self.event = event
        self.code = code

        lot = None

        if self.code is not None:
            lot = Lot.objects.filter(
                exhibition_code=self.code.upper())

        super().__init__(**kwargs)

        if lot:

            self.fields['lots'] = forms.ModelChoiceField(
                queryset=Lot.objects.filter(event=self.event),
                widget=forms.HiddenInput(),
                initial=lot.first(),
                required=False,
            )
        else:
            self.fields['lots'] = forms.ModelChoiceField(
                queryset=Lot.objects.filter(event=self.event),
                widget=forms.HiddenInput(),
                required=False,
            )

