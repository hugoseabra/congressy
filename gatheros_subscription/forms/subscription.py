""" Formulários de `Subscription` """
from django import forms

from gatheros_event.models import Person, Event
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
        )
        
    def __init__(self, event, **kwargs):
        self.event = event
        super().__init__(**kwargs)
        
        self.fields['lot'].queryset = event.lots.all()
        
    def clean_person(self):
        return Person.objects.get(pk=self.data['person'])

    def clean_lot(self):
        return Lot.objects.get(pk=self.data['lot'], event=self.event)
    
    def clean(self):
        cleaned_data = super().clean()
        
        person = cleaned_data.get('person')
        
        qs = Subscription.objects.filter(person=person, event=self.event)
        if qs.exists():
            self.cleaned_data.pop('person')
            self.add_error(
                forms.forms.NON_FIELD_ERRORS,
                'Esta inscrição já existe'
            )
        
        return cleaned_data
