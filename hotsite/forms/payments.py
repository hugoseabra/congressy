"""
    Formulário usado para pegar os dados de pagamento
"""

from django import forms


class PaymentForm(forms.Form):

    next_step = forms.IntegerField(
        widget=forms.HiddenInput()
    )

    previous_step = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=False,
    )

    lot = forms.IntegerField(
        widget=forms.HiddenInput()
    )

    person = forms.CharField(
        widget=forms.HiddenInput(),
        max_length=60,
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
