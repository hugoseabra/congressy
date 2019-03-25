""" Formulários de `Subscription` """

from django import forms

from gatheros_event.forms import PersonForm
from gatheros_event.helpers.event_business import is_paid_event
from gatheros_subscription.models import Subscription, FormConfig


class SubscriptionPersonForm(PersonForm):
    tag_info = forms.CharField(
        label='Informação para crachá',
        help_text='Informação customizada para sair no crachá do participante',
        required=False,
        max_length=16,
    )

    tag_group = forms.CharField(
        label='Informações de grupos',
        help_text='Informação customizada para sair no crachá do participante',
        required=False,
        max_length=16,
    )

    obs = forms.CharField(
        widget=forms.Textarea,
        label='Observações Gerais',
        required=False,
    )

    def check_requirements(self, lot=None):

        event_is_payable = False
        if lot:
            event_is_payable = is_paid_event(lot.event)

        if event_is_payable:
            try:
                config = lot.event.formconfig
            except AttributeError:
                config = FormConfig()
                config.event = lot.event
        else:
            config = FormConfig()
            config.event = lot.event

        country = self.data.get('person-country', 'BR')
        required_fields = ['gender', 'country']

        if event_is_payable or config.phone:
            required_fields.append('phone')
            required_fields.append('ddi')

        if event_is_payable:

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

        for field_name in required_fields:
            self.setAsRequired(field_name)

    def save(self, commit=True):
        return super().save(commit=commit)


class SubscriptionForm(forms.ModelForm):
    """ Formulário de lote. """

    class Meta:
        """ Meta """

        model = Subscription
        fields = (
            'origin',
            'lot',
            'person',
            'created_by',
            'tag_info',
            'tag_group',
            'obs',
        )

    def __init__(self, event, **kwargs):
        self.event = event
        super().__init__(**kwargs)

    def clean_lot(self):
        lot = self.cleaned_data.get('lot')
        if not lot:
            return lot

        if self.instance and self.instance.lot_id \
                and self.instance.lot_id == lot.pk:
            return lot

        num_subs = lot.subscriptions.filter(
            test_subscription=False,
            completed=True,
        ).exclude(status=Subscription.CANCELED_STATUS).count()

        origin = self.cleaned_data.get('origin')

        if origin != Subscription.DEVICE_ORIGIN_MANAGE:
            if num_subs and lot.limit and num_subs >= lot.limit:
                raise forms.ValidationError(
                    'Lote está lotado e não permite novas inscrições'
                )

        return lot

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

        if self.instance.origin == Subscription.DEVICE_ORIGIN_MANAGE:
            self.instance.completed = True

        return super().save(commit=commit)
