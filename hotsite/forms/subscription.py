"""
    Formulário usado para persistir as inscrições do hotsite
"""

from django import forms

from gatheros_event.models import Person, Event
from gatheros_subscription.models import Lot, Subscription


class SubscriptionForm(forms.Form):
    event = forms.IntegerField(
        widget=forms.HiddenInput()
    )

    lot = forms.IntegerField(
        widget=forms.HiddenInput()
    )

    person = forms.CharField(
        widget=forms.HiddenInput(),
        max_length=60,
    )

    def save(self):

        person = self.cleaned_data['person']
        event = self.cleaned_data['event']
        lot = self.cleaned_data['lot']

        try:
            subscription = Subscription.objects.get(
                person=person,
                event=event
            )
        except Subscription.DoesNotExist:
            subscription = Subscription(
                person=person,
                event=event,
                created_by=person.user.pk,
                origin=Subscription.DEVICE_ORIGIN_HOTSITE,
            )

        subscription.lot = lot

        return subscription.save()
