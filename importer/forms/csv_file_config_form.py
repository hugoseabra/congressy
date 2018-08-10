from django import forms

from importer.models import CSVFileConfig


class CSVFileConfigForm(forms.ModelForm):
    event = None

    class Meta:
        model = CSVFileConfig
        fields = [
            'event',
            'separator',
            'delimiter',
            'encoding',
        ]

        widgets = {
            'event': forms.HiddenInput(),
        }
