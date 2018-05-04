"""
    Formulário usado para pegar os dados da pessoa durante inscrições no
    hotsite
"""

from gatheros_event.forms import PersonForm
from gatheros_event.models import Person
from gatheros_subscription.models import FormConfig


class SubscriptionPersonForm(PersonForm):

    def __init__(self, user, lot, event, is_chrome=False, **kwargs):

        self.user = user
        self.lot = lot
        self.event = event

        try:
            person = Person.objects.get(user=user)
            kwargs.update({'instance': person})
        except Person.DoesNotExist:
            pass

        super().__init__(is_chrome, **kwargs)

        self.fields['email'].widget.attrs['disabled'] = 'disabled'
        self.fields['email'].disabled = True

        try:
            config = self.event.formconfig
        except AttributeError:
            config = FormConfig()
            config.event = self.event

        required_fields = ['gender']

        has_paid_lots = self.lot.price > 0 if self.lot.price else False

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

    def save(self, commit=True):
        self.instance.user = self.user
        return super().save(commit=commit)
