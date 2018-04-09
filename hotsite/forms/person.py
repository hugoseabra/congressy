"""
    Formulário usado para pegar os dados da pessoa durante inscrições no
    hotsite
"""
from django import forms

from gatheros_event.forms import PersonForm
from gatheros_subscription.models import FormConfig


class SubscriptionPersonForm(forms.Form, PersonForm):

    def __init__(self, is_chrome=False, **kwargs):

        super().__init__(is_chrome, **kwargs)

        try:
            config = self.event.formconfig
        except AttributeError:
            config = FormConfig()
            config.event = self.event

        required_fields = ['gender']

        has_paid_lots = lot.price > 0

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

        print('sdsadas')
