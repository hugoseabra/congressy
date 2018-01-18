""" Formulários de `Subscription` """
from django import forms

from gatheros_subscription.models import Subscription, Lot


class SubscriptionForm(forms.ModelForm):
    """ Formulário de lote. """

    class Meta:
        """ Meta """
        model = Subscription
        exclude = ('event', 'person', 'origin')

    def __init__(self, event, person=None, **kwargs):
        self.event = event
        self.person = person
        super().__init__(**kwargs)

        self.fields['lot'].queryset = Lot.objects.filter(event=self.event)

    def clean_lot(self):
        return Lot.objects.get(pk=self.data['lot'], event=self.event)

    def save(self, commit=True):
        self.instance.person = self.person
        self.instance.event = self.event
        self.instance.origin = Subscription.DEVICE_ORIGIN_WEB

        return super().save(commit=commit)

