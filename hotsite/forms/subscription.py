"""
    Formulário usado para persistir as inscrições do hotsite
"""

from datetime import datetime

from django import forms

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

    def clean_lot(self):
        try:
            lot = Lot.objects.get(pk=self.cleaned_data['lot'],
                                  event_id=self.cleaned_data['event'])
        except Lot.DoesNotExist:
            raise forms.ValidationError('Lote não pertence a este evento.')

        subscriptions = Subscription.objects.filter(
            lot_id=lot.pk,
            test_subscription=False,
            completed=True,
        ).count()

        if lot.limit and subscriptions > lot.limit:
            raise forms.ValidationError('Lote está lotado e não permite novas '
                                        'inscrições')

        if lot.date_end < datetime.now():
            raise forms.ValidationError('Lote já está finalizado e não '
                                        'permite novas inscrições.')

        return lot

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
