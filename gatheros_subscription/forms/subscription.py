""" Formulários de `Subscription` """
from datetime import datetime

from django import forms

from gatheros_event.forms import PersonForm
from gatheros_subscription.models import Subscription, Lot, FormConfig
from .validators import validate_csv_only_file


class SubscriptionPersonForm(PersonForm):
    def check_requirements(self, lot=None):

        has_paid_lots = False
        if lot:
            has_paid_lots = lot.price > 0 if lot.price else False

        if has_paid_lots:
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

        if has_paid_lots or config.phone:
            required_fields.append('phone')

        if has_paid_lots:
            required_fields.append('street')
            required_fields.append('village')

            if country == 'BR':
                required_fields.append('zip_code')
            else:
                required_fields.append('zip_code_international')

            if country == 'BR':
                required_fields.append('city')
            else:
                required_fields.append('city_international')
                required_fields.append('state_international')

        if not has_paid_lots \
                and not config.address_show \
                and config.city is True:

            if country == 'BR':
                required_fields.append('city')
            else:
                required_fields.append('city_international')

        if has_paid_lots or config.cpf_required:
            if country == 'BR':
                required_fields.append('cpf')
            else:
                required_fields.append('international_doc')
                required_fields.append('state_international')

        if has_paid_lots or config.birth_date_required:
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
            'lot',
            'person',
            'origin',
            'created_by',
            # 'completed',
        )

    allow_lot_edit = True

    def __init__(self, event, **kwargs):
        self.event = event

        is_new = not kwargs.get('instance')

        super().__init__(**kwargs)

        origin = self.data.get('origin')

        self.fields['lot'].queryset = event.lots.all()
        if is_new is False and origin != Subscription.DEVICE_ORIGIN_MANAGE:
            self.fields['lot'].disabled = True
            self.allow_lot_edit = False

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

        if self.instance.origin == Subscription.DEVICE_ORIGIN_MANAGE:
            self.instance.completed = True

        return super().save(commit=commit)


class SubscriptionAttendanceForm(forms.Form):
    """ Formulário de credenciamento de Inscrições. """

    def __init__(self, instance=None, *args, **kwargs):
        self.instance = instance
        super(SubscriptionAttendanceForm, self).__init__(*args, **kwargs)

    def attended(self, attended):
        """ Persiste atendimento de acordo com parâmetro. """
        self.instance.attended_on = datetime.now() if attended else None
        self.instance.attended = attended
        self.instance.save()


class SubscriptionCSVUploadForm(forms.Form):

    ENCODING_UTF8 = "utf-8"
    ENCODING_8859_1 = "iso-8859-1"

    ENCODING_CHOICES  = (
        (ENCODING_UTF8, "UTF-8"),
        (ENCODING_8859_1, "ISO 8859-1(Latim)")
    )

    csv_file = forms.FileField(
        validators=[validate_csv_only_file],
        label="Arquivo CSV:"
    )

    separator = forms.CharField(
        label="Separador",
        max_length=1,
        required=False,
        initial='"',
    )

    delimiter = forms.CharField(
        label="Delimitador",
        max_length=1,
        required=False,
        initial=",",
    )

    encoding = forms.ChoiceField(
        label="Tipo de Codificação",
        required=False,
        choices=ENCODING_CHOICES,
        initial=ENCODING_UTF8,
    )
