""" Formulários de `Subscription` """
from django import forms

from gatheros_subscription.models import Subscription, Lot


class SubscriptionForm(forms.ModelForm):
    """ Formulário de lote. """

    class Meta:
        """ Meta """

        model = Subscription
        fields = (
            'lot',
            'person',
            'origin',
            'created_by',
            # 'completed',
        )

    def __init__(self, event, **kwargs):
        self.event = event
        super().__init__(**kwargs)

        self.fields['lot'].queryset = event.lots.all()

    def clean_lot(self):
        try:
            return Lot.objects.get(pk=self.data['lot'], event=self.event)
        except Lot.DoesNotExist:
            raise forms.ValidationError('Lote não pertence a este evento.')

    def clean(self):
        cleaned_data = super().clean()

        if not self.instance or not self.instance.pk:
            person = cleaned_data.get('person')

            qs = Subscription.objects.filter(person=person, event=self.event)
            if qs.exists():
                cleaned_data.pop('person')
                self.add_error(
                    forms.forms.NON_FIELD_ERRORS,
                    'Esta inscrição já existe'
                )

        return cleaned_data

    def save(self, commit=True):

        if self.instance.free is True:
            self.instance.status = Subscription.CONFIRMED_STATUS

        return super().save(commit=commit)
