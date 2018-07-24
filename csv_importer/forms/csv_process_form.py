from django import forms


class CSVProcessForm(forms.Form):
    create_subscriptions = forms.BooleanField(
        widget=forms.HiddenInput,
        required=False,
    )
    create_error_xls = forms.BooleanField(
        widget=forms.HiddenInput,
        required=False,
    )

    create_subscriptions_and_error_xls = forms.BooleanField(
        widget=forms.HiddenInput,
        required=False,
    )
