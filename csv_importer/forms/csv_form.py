from django import forms

from csv_importer.models import CSVImportFile


class CSVForm(forms.ModelForm):
    event = None

    class Meta:
        model = CSVImportFile
        fields = [
            'event',
            'separator',
            'delimiter',
            'encoding',
        ]

        widgets = {
            'event': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class CSVFileForm(forms.ModelForm):
    event = None

    class Meta:
        model = CSVImportFile
        fields = [
            'event',
            'csv_file',
        ]

        widgets = {
            'event': forms.HiddenInput(),
        }

        labels = {
            'csv_file': 'Arquivo CSV:'
        }
