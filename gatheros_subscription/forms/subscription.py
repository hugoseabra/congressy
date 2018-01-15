""" Formulários de `Subscription` """
from django import forms

from gatheros_subscription.models import Subscription


class SubscriptionForm(forms.ModelForm):
    """ Formulário de lote. """
    class Meta:
        """ Meta """
        model = Subscription
        fields = '__all__'
