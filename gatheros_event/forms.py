from django import forms

from core.fields import MultiEmailField
from .models import Organization


class InvitationForm(forms.Form):
    organization = forms.ModelChoiceField(
        queryset=Organization.objects.all(),
        empty_label='-----',
        label='Organização'
    )
    emails = MultiEmailField(label='Emails')

    def __init__(self, user, data=None, *args, **kwargs):
        super(InvitationForm, self).__init__(data=data, *args, **kwargs)

        if not user.is_superuser:
            self.fields['organization'].queryset = Organization.objects.filter(
                members__person__user=user
            )

    def save(self):
        pass
