from django import forms
from scientific_work.models import Work


class NewWorkForm(forms.ModelForm):
    subscription = None

    def __init__(self, subscription, *args, **kwargs):
        self.subscription = subscription
        super().__init__(*args, **kwargs)

    class Meta:
        model = Work
        exclude = [
            'subscription',
        ]

    def clean_accepts_terms(self):
        terms = self.cleaned_data['accepts_terms']
        if not terms:
            raise forms.ValidationError('Você deve aceitar os termos e '
                                        'condições para submeter.')
        return terms

    def save(self, commit=True):
        self.instance.subscription = self.subscription
        return super().save(commit)


