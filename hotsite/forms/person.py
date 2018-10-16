"""
    Formulário usado para pegar os dados da pessoa durante inscrições no
    hotsite
"""

from gatheros_event.forms import PersonForm
from gatheros_event.helpers.event_business import is_paid_event
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

        self.fields['name'].widget.attrs['disabled'] = 'disabled'
        self.fields['name'].disabled = True

        self.fields['state_international'].label = "Estado/Província/Região"
        self.fields['address_international'].label = "Endereço"


        if self.instance.pk:
            if self.instance.name:
                self.fields['name'].disabled = True
                self.fields['name'].widget.attrs['data-toggle'] = 'tooltip'
                self.fields['name'].widget.attrs['title'] = \
                    'Por questões de segurança, o nome não pode ser' \
                    ' alterado. Caso você deseja fazer alguma alteração,' \
                    ' solicite ao suporte técnico da Congressy.'

            if self.instance.email:
                self.fields['email'].disabled = True
                self.fields['email'].widget.attrs['data-toggle'] = 'tooltip'
                self.fields['email'].widget.attrs['title'] = \
                    'Por questões de segurança, o e-mail não pode ser' \
                    ' alterado.'

            if self.instance.international_doc:
                international_doc_f = self.fields['international_doc']
                international_doc_f.disabled = True
                international_doc_f.widget.attrs['data-toggle'] = 'tooltip'
                international_doc_f.widget.attrs['title'] = \
                    'Por questões de segurança, o número do documento não' \
                    ' pode ser alterado.'
                self.fields['international_doc'] = international_doc_f

            if self.instance.cpf:
                self.fields['cpf'].disabled = True
                self.fields['cpf'].widget.attrs['data-toggle'] = 'tooltip'
                self.fields['cpf'].widget.attrs['title'] = \
                    'Por questões de segurança, o CPF não pode ser alterado.'

        try:
            config = self.event.formconfig
        except AttributeError:
            config = FormConfig()
            config.event = self.event

        country = self.data.get('person-country', 'BR')
        required_fields = ['gender', 'country']

        event_is_payable = is_paid_event(self.event)

        if event_is_payable or config.phone:
            required_fields.append('phone')

        if event_is_payable or config.address_show:
            if country == 'BR':
                required_fields.append('zip_code')
                required_fields.append('street')
                required_fields.append('village')
                required_fields.append('city')
            else:
                required_fields.append('city_international')
                required_fields.append('address_international')

        if not event_is_payable \
                and not config.address_show \
                and config.city is True:

            if country == 'BR':
                required_fields.append('city')
            else:
                required_fields.append('city_international')
                required_fields.append('address_international')

        if event_is_payable or config.cpf_required:
            if country == 'BR':
                required_fields.append('cpf')
            else:
                required_fields.append('international_doc')

        if event_is_payable or config.birth_date_required:
            required_fields.append('birth_date')

        if config.institution_required:
            required_fields.append('institution')

        if config.institution_cnpj_required:
            required_fields.append('institution_cnpj')

        if config.function_required:
            required_fields.append('function')

        for field_name in required_fields:
            self.setAsRequired(field_name)

    def save(self, commit=True):
        self.instance.user = self.user
        return super().save(commit=commit)
