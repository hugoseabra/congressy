from django import forms


class CSVProcessForm(forms.Form):
    create_subscriptions = forms.BooleanField(
        widget=forms.HiddenInput,
        required=False,
    )