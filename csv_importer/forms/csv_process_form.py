from django import forms


class CSVProcessForm(forms.Form):

    confirm = forms.BooleanField(
        label="Certeza que deseja desejas essas inscrições?"
    )
