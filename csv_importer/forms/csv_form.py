from django import forms

from csv_importer.models import CSVImportFile


class CSVForm(forms.ModelForm):
    class Meta:
        model = CSVImportFile
        fields = '__all__'
