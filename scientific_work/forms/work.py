from django import forms
from scientific_work.models import Work


class NewWorkForm(forms.ModelForm):

    class Meta:
        model = Work
        fields = '__all__'

    author = forms.CharField(
            max_length=255,
            label="Autores",
    )


    def clean_accepts_terms(self):
        terms = self.cleaned_data['accepts_terms']
        if not terms:
            raise forms.ValidationError('Você deve aceitar os termos e '
                                        'condições para submeter.')
