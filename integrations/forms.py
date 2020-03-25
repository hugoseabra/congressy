from django import forms

from .models import MailChimpIntegration


class MailChimpIntegrationForm(forms.ModelForm):
    class Meta:
        model = MailChimpIntegration
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.api_key:
            self.fields['api_key'].widget.attrs['readonly'] = True

        self.fields['list_id'].widget = forms.Select(
            choices=(
                (None, '- SElect - '),
            ),
        )
