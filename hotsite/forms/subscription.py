"""
    Formulário usado para persistir as inscrições do hotsite
"""

from django import forms

from gatheros_event.models import Person, Event
from gatheros_subscription.models import Lot, Subscription


class SubscriptionForm(forms.Form):
    event = None
    event_lot = None
    person = None

    previous_step = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=False,
    )

    def __init__(self, lot, person, event, **kwargs):

        if not isinstance(lot, Lot):
            raise TypeError('lot não é um objeto do tipo Lot')

        if not isinstance(person, Person):
            raise TypeError('person não é um objeto do tipo Person')

        if not isinstance(event, Event):
            raise TypeError('event não é um objeto do tipo Event')

        self.event = event
        self.event_lot = lot
        self.person = Person

        super().__init__(**kwargs)

    def save(self):

        try:
            subscription = Subscription.objects.get(
                person=self.person,
                event=self.event
            )
        except Subscription.DoesNotExist:
            subscription = Subscription(
                person=self.person,
                event=self.event,
                created_by=self.person.user.pk
            )

        subscription.lot = self.lot

        return subscription.save()
