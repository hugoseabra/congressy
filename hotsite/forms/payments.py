"""
    Formulário usado para pegar os dados de pagamento
"""

from django import forms


class PaymentForm(forms.Form):

    next_step = forms.IntegerField(
        widget=forms.HiddenInput()
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
