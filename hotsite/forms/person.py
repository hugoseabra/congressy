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

    current_step = forms.IntegerField(
        widget=forms.HiddenInput(),
        initial=2,
    )

    coupon_code = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=False,
    )

    def __init__(self, lot,  event, coupon_code=None, is_chrome=False, **kwargs):

        if not isinstance(lot, Lot):
            raise TypeError('lot não é do tipo Lot')

        self.event = event
        self.event_lot = lot
        self.coupon_code = coupon_code

        super().__init__(is_chrome, **kwargs)

        self.fields['lot'] = forms.IntegerField(
            initial=self.event_lot.pk,
            widget=forms.HiddenInput(),
        )

        if self.coupon_code:
            self.fields['coupon_code'].initial = self.coupon_code
        else:
            self.fields['coupon_code'].inital = ''

        if self.event_lot.event_survey:
            self.fields['next_step'].initial = 3
        elif self.event_lot.price and self.event_lot.price > 0:
            self.fields['next_step'].initial = 4
        else:
            self.fields['next_step'].initial = 5

        try:
            config = self.event.formconfig
        except AttributeError:
            config = FormConfig()
            config.event = self.event

        required_fields = ['gender']

        has_paid_lots = self.event_lot.price > 0 if self.event_lot.price \
            else False

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
