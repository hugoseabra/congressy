"""
    Formulário usado para selecionar o lote do evento.
"""

from django import forms

from gatheros_subscription.models import Lot


class PrivateLotForm(forms.Form):

    def __init__(self, **kwargs):
        self.event = kwargs.get('initial').get('event')
        self.code = kwargs.get('initial').get('code')

        lot = None

        if self.code is not None:
            try:
                lot = Lot.objects.get(exhibition_code=self.code.upper())
            except Lot.DoesNotExist:
                pass

        super().__init__(**kwargs)

        queryset = Lot.objects.filter(event=self.event)

        available_lots = [lot for lot in queryset if lot.places_remaining > 0]

        self.fields['lots'] = forms.ModelChoiceField(
            queryset=queryset,
            choices=available_lots,
            widget=forms.HiddenInput(),
            required=False,
        )
        
        if lot:
            self.fields['lots'].initial = lot
