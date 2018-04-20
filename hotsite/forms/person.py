"""
    Formulário usado para pegar os dados da pessoa durante inscrições no
    hotsite
"""

from django.utils.datastructures import MultiValueDictKeyError

from gatheros_event.forms import PersonForm
from gatheros_event.models import Person
from gatheros_subscription.models import FormConfig, Lot


class SubscriptionPersonForm(PersonForm):

    def __init__(self, is_chrome=False, **kwargs):

        self.lot = kwargs.get('initial').get('lot')
        self.event = kwargs.get('initial').get('event')

        user = kwargs.get('initial').get('user')

        if user:
            try:
                person = Person.objects.get(user=user)
                kwargs.update({'instance': person})
            except Person.DoesNotExist:
                pass

        if not isinstance(self.lot, Lot):
            try:
                self.lot = Lot.objects.get(pk=self.lot, event=self.event)
            except Lot.DoesNotExist:
                message = 'Não foi possivel resgatar um Lote ' \
                          'a partir das referencias: lot<{}> e evento<{}>.' \
                    .format(self.lot, self.event)
                raise TypeError(message)

        super().__init__(is_chrome, **kwargs)

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

    def clean_email(self):

        if self.data.get('email') or self.initial.get('email'):
            try:
                email = self.data.get('email')
                if not email:
                    email = self.data.get('person-email')
            except MultiValueDictKeyError:
                email = self.initial.get('email')
                if not email:
                    email = self.data.get('person-email')
            return email.lower()

        return None
