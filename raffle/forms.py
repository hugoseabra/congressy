from django import forms

from raffle.models import Raffle, Winner


class RaffleForm(forms.ModelForm):
    class Meta:
        model = Raffle
        exclude = ('event',)

    def __init__(self, event, *args, **kwargs):
        self.event = event
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        self.instance.event = self.event
        return super().save(commit)


class WinnerForm(forms.ModelForm):
    class Meta:
        model = Winner
        exclude = ('event',)
        widgets = {
            'subscription': forms.HiddenInput
        }

    def __init__(self, event, *args, **kwargs):
        self.event = event
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        self.instance.event = self.event
        return super().save(commit)
