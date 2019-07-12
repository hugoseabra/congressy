"""
    Formulário usado para persistir as inscrições do hotsite
"""

from datetime import datetime

from django import forms

from gatheros_subscription.models import Subscription
from ticket.models import Lot


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

    def __init__(self, *args, **kwargs):
        self.subscription = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        event = self.cleaned_data['event']
        lot_pk = self.cleaned_data['lot']
        person = self.cleaned_data['person']

        try:
            self.subscription = Subscription.objects.get(
                person_id=person.pk,
                event_id=event.pk,
            )

        except Subscription.DoesNotExist:
            self.subscription = Subscription(
                person_id=person.pk,
                event_id=event.pk,
                created_by=person.user.pk,
                origin=Subscription.DEVICE_ORIGIN_HOTSITE,
            )

        if self.subscription.ticket_lot_id == lot_pk:
            # Lote não mudou
            return cleaned_data

        try:
            lot = Lot.objects.get(pk=lot_pk, event_id=event)
        except Lot.DoesNotExist:
            raise forms.ValidationError('Lote não pertence a este evento.')

        if datetime.now() >= lot.date_end:
            raise forms.ValidationError('Lote já está finalizado e não '
                                        'permite novas inscrições.')

        num_subs = Subscription.objects.filter(
            lot_id=lot.pk,
            test_subscription=False,
            completed=True,
        ).exclude(status=Subscription.CANCELED_STATUS).count()

        if num_subs and lot.limit and num_subs >= lot.limit:
            raise forms.ValidationError('Lote está lotado e não permite novas '
                                        'inscrições')

        self.subscription.ticket_lot = lot

        return cleaned_data

    def save(self):
        return self.subscription.save()
