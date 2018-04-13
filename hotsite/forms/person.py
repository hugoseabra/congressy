"""
    Formulário usado para pegar os dados da pessoa durante inscrições no
    hotsite
"""
from datetime import datetime

from django import forms
from django.forms import BaseModelForm

from gatheros_event.forms import PersonForm
from gatheros_subscription.models import FormConfig, Lot


class SubscriptionPersonForm(PersonForm):

    event = None
    event_lot = None

    next_step = forms.IntegerField(
        widget=forms.HiddenInput()
    )

    previous_step = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=False,
    )

    coupon_code = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=False,
    )

    def __init__(self, lot, event, is_chrome=False, **kwargs):

        if not isinstance(lot, Lot):
            raise TypeError('lot não é do tipo Lot')

        self.event = event
        self.event_lot = lot

        super().__init__(is_chrome, **kwargs)

        self.fields['lots'] = forms.ModelChoiceField(
            queryset=Lot.objects.filter(event=self.event,
                                        date_start__lte=datetime.now(),
                                        date_end__gte=datetime.now(),
                                        private=False,
                                        ),

            widget=forms.HiddenInput(),
        )

        try:
            config = self.event.formconfig
        except AttributeError:
            config = FormConfig()
            config.event = self.event

        required_fields = ['gender']

        has_paid_lots = self.event_lot.price > 0

        if has_paid_lots or config.phone:
            required_fields.append('phone')

        if has_paid_lots or config.address_show:
            required_fields.append('street')
            required_fields.append('village')
            required_fields.append('zip_code')
            required_fields.append('city')

        if not has_paid_lots \
                and not config.address_show \
                and config.city is True:
            required_fields.append('city')

        if has_paid_lots or config.cpf_required:
            required_fields.append('cpf')

        if has_paid_lots or config.birth_date_required:
            required_fields.append('birth_date')

        for field_name in required_fields:
            self.setAsRequired(field_name)
