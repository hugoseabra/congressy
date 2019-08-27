"""
Formulários de Event
"""
import os
from datetime import datetime, timedelta

from django import forms
from django.core.exceptions import NON_FIELD_ERRORS
from django.db.transaction import atomic
from django.shortcuts import get_object_or_404

from core.forms.widgets import SplitDateTimeBootsrapWidget
from core.util import model_field_slugify, ReservedSlugException
from gatheros_event.models import Event, Member, Info, Place
from gatheros_event.models import Organization
from gatheros_event.models.constants import CONGRESSY_PERCENT_10_0
from gatheros_subscription.models import FormConfig, LotCategory


class DateTimeInput(forms.DateTimeInput):
    input_type = 'tel'


class EventForm(forms.ModelForm):
    """Formulário principal de evento"""

    has_optionals = forms.BooleanField(
        label='Opcionais',
        help_text='Você irá vender, opcionais como: hospedagem, alimentação, '
                  'camisetas?',
        required=False,
    )
    has_extra_activities = forms.BooleanField(
        label='Atividades extras',
        help_text='Seu evento terá: workshops, minicursos?',
        required=False,
    )

    has_checkin = forms.BooleanField(
        label='Checkin',
        help_text='Deseja realizar o checkin com nosso App gratuito?',
        required=False,
    )

    has_certificate = forms.BooleanField(
        label='Certificado',
        help_text='Seu evento terá entrega de Certificados ?',
        required=False,
    )

    has_survey = forms.BooleanField(
        label='Formulário Personalizado',
        help_text='Seu evento terá formulário com perguntas personalizadas ?',
        required=False,
    )

    class Meta:
        model = Event
        fields = [
            'organization',
            'category',
            'name',
            'date_start',
            'date_end',
            'rsvp_type',
            'expected_subscriptions',
            'is_scientific'
        ]

        widgets = {
            'organization': forms.HiddenInput,
            'subscription_type': forms.RadioSelect,
            'date_start': SplitDateTimeBootsrapWidget,
            'date_end': SplitDateTimeBootsrapWidget,
        }

    def __init__(self, user, lang='pt-br', *args, **kwargs):
        self.user = user

        instance = kwargs.get('instance')

        super(EventForm, self).__init__(*args, **kwargs)

        self.fields['expected_subscriptions'].required = True
        if instance is None:
            self._configure_organization_field()

    def _configure_organization_field(self):
        orgs = []
        for member in self.user.person.members.filter():
            organization = member.organization

            can_add = self.user.has_perm(
                'gatheros_event.can_add_event',
                organization
            )
            if not can_add:
                continue

            orgs.append((organization.pk, organization.name,))

        self.fields['organization'].widget = forms.Select()
        self.fields['organization'].choices = orgs
        self.fields['organization'].label = 'Realizador'

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            return name

        if not self.instance.pk:
            instance = Event()

            try:
                model_field_slugify(
                    model_class=Event,
                    instance=instance,
                    string=name,
                )

            except ReservedSlugException:
                raise forms.ValidationError(
                    'Verifique o nome do seu evento. Este nome não poderá ser'
                    ' usado.'
                )

        return name

    def clean_date_end(self):
        date_end = self.cleaned_data.get('date_end')
        if not date_end:
            date_end = datetime.now() - timedelta(minutes=1)

        date_start = self.cleaned_data.get('date_start')
        if date_start and date_start > date_end:
            raise forms.ValidationError(
                'Data inicial deve ser anterior a data final.'
            )

        return date_end


class EventDuplicationForm(forms.Form):
    """Formulário de duplicação de evento"""

    event_name = forms.CharField(
        max_length=255,
        required=True,
        label='Nome do evento',
        help_text='Você definir um nome diferente para o evento',
    )

    date_start = forms.DateTimeField(
        label='Data/hora inicial do evento',
        help_text='Data e hora em que evento irá iniciar',
        widget=SplitDateTimeBootsrapWidget,
        required=True,
        input_formats=[
            '%Y-%m-%d %H:%M:%S',
            '%d/%m/%Y %H:%M:%S',
        ],
    )

    date_end = forms.DateTimeField(
        label='Data/hora final do evento',
        help_text='Data e hora em que evento irá encerrar',
        widget=SplitDateTimeBootsrapWidget,
        required=True,
        input_formats=[
            '%Y-%m-%d %H:%M:%S',
            '%d/%m/%Y %H:%M:%S',
        ],
    )

    organization = forms.ChoiceField(
        widget=forms.Select(),
        label='Realizador',
        required=True,
        choices=list(),
    )

    duplicate_categories_lots = forms.BooleanField(
        label='Duplicar Categorias / Lotes',
        required=False,
    )

    duplicate_addon_services = forms.BooleanField(
        label='Duplicar atividades extras',
        required=False,
    )

    duplicate_addon_products = forms.BooleanField(
        label='Duplicar opcionais',
        required=False,
    )

    duplicate_surveys = forms.BooleanField(
        label='Duplicar formulários',
        required=False,
    )

    duplicate_certificate = forms.BooleanField(
        label='Duplicar certificado',
        required=False,
    )

    duplicate_attendance_services = forms.BooleanField(
        label='Duplicar Serviços de atendimento',
        required=False,
    )

    def __init__(self, person, event, *args, **kwargs):
        self.person = person
        self.event = event

        kwargs.update({'initial': {
            'event_name': event.name,
            'organization': event.organization_id,
            'date_start': event.date_start,
            'date_end': event.date_end,
            'duplicate_categories_lots': True,
            'duplicate_surveys': True,
            'duplicate_certificate': True,
            'duplicate_attendance_services': True,
            'duplicate_addon_services': True,
            'duplicate_addon_products': True,
        }})

        super().__init__(*args, **kwargs)

        self._configure_organization_field()

    def _configure_organization_field(self):
        orgs = []
        for member in self.person.members.filter(active=True):
            organization = member.organization

            can_add = self.person.user.has_perm(
                'gatheros_event.can_add_event',
                organization
            )
            if not can_add:
                continue

            orgs.append((organization.pk, organization.name,))

        self.fields['organization'].choices = orgs

    def clean_organization(self):
        org_id = self.cleaned_data.get('organization')

        if not org_id:
            return None

        return Organization.objects.get(pk=org_id)

    def clean_date_end(self):
        date_end = self.cleaned_data.get('date_end')
        if not date_end:
            date_end = datetime.now() - timedelta(minutes=1)

        date_start = self.cleaned_data.get('date_start')
        if date_start and date_start > date_end:
            raise forms.ValidationError(
                'Data inicial deve ser anterior a data final.'
            )

        return date_end

    def clean(self):
        cleaned_data = super().clean()

        if self.event.organization.is_member(self.person) is False:
            self.add_error(
                NON_FIELD_ERRORS,
                'Você não faz parte da organização deste evento.'
            )

        return cleaned_data

    def save(self):
        with atomic():
            c_data = self.cleaned_data

            # Deve-se considerar configuração administrativa do evento
            feature_config = self.event.feature_configuration

            feat_survey = feature_config.feature_survey is True
            feat_checkin = feature_config.feature_checkin is True
            feat_cert = feature_config.feature_certificate is True
            feat_addon_prod = feature_config.feature_products is True
            feat_addon_serv = feature_config.feature_services is True
            feat_internal_sub = \
                feature_config.feature_internal_subscription is True
            feat_boleto_exp_lot_exp = \
                feature_config.feature_boleto_expiration_on_lot_expiration

            dup_survey = \
                feat_survey is True and c_data.get('duplicate_surveys') is True

            dup_att_serv = \
                feat_checkin is True \
                and c_data.get('duplicate_attendance_services') is True

            dup_cert = \
                feat_cert is True and c_data.get(
                    'duplicate_certificate') is True

            dup_addon_prod = \
                feat_addon_prod is True \
                and c_data.get('duplicate_addon_products') is True

            dup_addon_serv = \
                feat_addon_serv is True \
                and c_data.get('duplicate_addon_services') is True

            dup_cat_lots = c_data.get('duplicate_categories_lots') is True

            # Buscando referência nova para evento
            event = Event.objects.get(pk=self.event.pk)
            event.pk = None
            event.slug = None
            event.organization = self.cleaned_data.get('organization')
            event.name = self.cleaned_data.get('event_name')
            event.date_start = self.cleaned_data.get('date_start')
            event.date_end = self.cleaned_data.get('date_end')

            # Reseta dados iniciais padrão
            event.congressy_percent = CONGRESSY_PERCENT_10_0
            event.boleto_limit_days = 3  # default

            event.save()

            if dup_cat_lots is True:
                # Exclui categoria e lote criado por padrão.
                event.lots.first().delete()
                event.lot_categories.first().delete()

            # FEATURE CONFIGURATION
            feature_config2 = event.feature_configuration
            feature_config2.feature_survey = feat_survey
            feature_config2.feature_checkin = feat_checkin
            feature_config2.feature_certificate = feat_cert
            feature_config2.feature_products = feat_addon_prod
            feature_config2.feature_services = feat_addon_serv
            feature_config2.feature_internal_subscription = feat_internal_sub
            feature_config2.feat_boleto_exp_lot_exp = feat_boleto_exp_lot_exp

            # Features ativadas por padrão
            feature_config2.feature_multi_lots = True

            # Features desativadas por padrão
            feature_config2.feature_import_via_csv = False
            feature_config2.feature_manual_payments = False
            feature_config2.feature_raffle = False

            feature_config2.save()

            # FEATURE MANAGEMENT
            feat_manage = self.event.feature_management

            feat_manage2 = event.feature_management
            feat_manage2.checkin = dup_att_serv and feat_manage.checkin
            feat_manage2.survey = dup_survey and feat_manage.survey
            feat_manage2.certificate = dup_cert and feat_manage.certificate
            feat_manage2.services = dup_addon_serv and feat_manage.services
            feat_manage2.products = dup_addon_prod and feat_manage.products

            # Features desativadas por padrão
            feat_manage2.raffle = False

            feat_manage2.save()

            try:
                info = Info.objects.get(event_id=self.event.pk)
                info.pk = None
                info.event_id = event.pk

            except Info.DoesNotExist:
                info = Info(event_id=event.pk)

            info.save()

            try:
                form_config = FormConfig.objects.get(event_id=self.event.pk)
                form_config.pk = None
                form_config.event_id = event.pk

            except FormConfig.DoesNotExist:
                form_config = FormConfig(event_id=event.pk)

            form_config.save()

            try:
                place = Place.objects.get(event_id=self.event.pk)
                place.pk = None
                place.event_id = event.pk

            except Place.DoesNotExist:
                place = Place(event_id=event.pk)

            place.save()

            cat_qs = self.event.lot_categories

            if not cat_qs.count():
                # Suporte a eventos muitos antigos - 1.3.x
                LotCategory.objects.create(
                    name='Geral',
                    event_id=self.event.pk,
                )

            for cat in cat_qs.all():

                lots = cat.lots.all()

                if dup_addon_serv:
                    services = cat.service_optionals.all()

                if dup_addon_prod:
                    products = cat.product_optionals.all()

                if dup_cat_lots is True:
                    cat.pk = None
                    cat.event_id = event.pk
                    cat.save()

                    for lot in lots:
                        lot.pk = None
                        lot.category_id = cat.pk
                        lot.event_id = event.pk
                        lot.event_survey_id = None
                        # Se for privado, renova o código
                        lot.exhibition_code = None
                        lot.save()

                if dup_addon_serv:
                    for serv in services:
                        theme = serv.theme
                        theme.event_id = event.pk
                        theme.save()

                        serv.pk = None
                        serv.theme_id = theme.pk
                        serv.lot_category_id = cat.pk
                        serv.published = False
                        serv.save()

                if dup_addon_prod:
                    for serv in products:
                        serv.pk = None
                        serv.lot_category_id = cat.pk
                        serv.published = False
                        serv.save()

            if dup_cert and hasattr(self.event, 'certificate'):
                certificate = self.event.certificate
                certificate.pk = None
                certificate.event_id = event.pk
                certificate.save()

            if dup_survey:
                for event_survey in self.event.surveys.all():

                    survey = event_survey.survey

                    questions = survey.questions.all()

                    survey.pk = None
                    survey.save()

                    event_survey.pk = None
                    event_survey.event_id = event.pk
                    event_survey.survey_id = survey.pk
                    event_survey.save()

                    for question in questions:
                        if question.has_options:
                            options = question.options.all()
                        else:
                            options = list()

                        question.pk = None
                        question.survey_id = survey.pk
                        question.save()

                        for option in options:
                            option.pk = None
                            option.question_id = question.pk
                            option.save()

            if dup_att_serv:
                att_serv_qs = self.event.attendance_services.all()

                if att_serv_qs.count() > 0:

                    first_att_serv = att_serv_qs.order_by('id').first()

                    first_att_serv2 = \
                        event.attendance_services.all().order_by('id').first()

                    first_att_serv2.name = first_att_serv.name
                    first_att_serv2.checkout_enabled = \
                        first_att_serv.checkout_enabled
                    first_att_serv2.with_certificate = \
                        first_att_serv.with_certificate
                    first_att_serv2.printing_queue_webhook = None
                    first_att_serv2.printer_number = None
                    first_att_serv2.pwa_pin = None
                    first_att_serv2.accreditation = True
                    first_att_serv2.save()

                    for att_serv in att_serv_qs:
                        if att_serv.pk == first_att_serv.pk:
                            continue

                        att_serv.pk = None
                        att_serv.accreditation = False
                        att_serv.event_id = event.pk
                        att_serv.save()

            event.published = False
            event.save()

            return event


class EventEditDatesForm(forms.ModelForm):
    """Formulário de edição de datas de evento"""

    class Meta:
        model = Event
        fields = [
            'date_start',
            'date_end',
        ]


class EventEditSubscriptionTypeForm(forms.ModelForm):
    """Formulário de edição de Tipo de Inscrição de evento"""

    class Meta:
        model = Event
        fields = [
            'subscription_type',
            'subscription_offline',
        ]


class EventPublicationForm(forms.ModelForm):
    """Formulário de edição de publicação de evento"""

    class Meta:
        model = Event
        fields = [
            'published',
        ]

    def clean_published(self):
        """Limpa campo 'published'"""
        published = self.data['published']
        if isinstance(published, str):
            published = published == '1'

        return published


class EventBannerForm(forms.ModelForm):
    """Formulário de upload de imagens de evento."""

    class Meta:
        model = Event
        fields = [
            'banner_small',
            'banner_top',
            'banner_slide',
        ]

    def clean_banner_small(self):
        """ Limpa campo banner_small """
        self._clear_file('banner_small')
        return self.cleaned_data['banner_small']

    def clean_banner_top(self):
        """ Limpa campo banner_top """
        self._clear_file('banner_top')
        return self.cleaned_data['banner_top']

    def clean_banner_slide(self):
        """ Limpa campo banner_slide """
        self._clear_file('banner_slide')
        return self.cleaned_data['banner_slide']

    def _clear_file(self, field_name):
        """Removes files from model"""

        if field_name not in self.changed_data:
            return

        field = getattr(self.instance, field_name)
        if not field:
            return

        path = os.path.dirname(field.file.name)

        # Executa lógica de remoção que trata cache e outros resizes
        field.delete()

        # Remove diretórios vazios
        if not os.listdir(path):
            os.rmdir(path)


class EventSocialMediaForm(forms.ModelForm):
    """Formulário de edição de local de evento."""

    class Meta:
        """ Meta """
        model = Event
        fields = [
            'website',
            'facebook',
            'linkedin',
            'twitter',
            'skype',
        ]


class EventTransferForm(forms.Form):
    """
    Formulário de Transferência de propriedade de evento entre organizações.
    """
    instance = None
    user = None

    organization_to = forms.ChoiceField(label='Para')

    def __init__(self, user, instance, *args, **kwargs):
        self.user = user
        self.instance = instance
        super(EventTransferForm, self).__init__(*args, **kwargs)
        self._populate()

    def _populate(self):
        current_org = self.instance.organization
        members = self.user.person.members.filter(group=Member.ADMIN).order_by(
            '-organization__internal',
            'organization__name'
        )

        organizations = [
            (member.organization.pk, member.organization.name)
            for member in members if member.organization.pk != current_org.pk
        ]
        self.fields['organization_to'].choices = organizations

    def clean(self):
        """ Limpa campos. """
        organization = get_object_or_404(
            Organization,
            pk=self.data['organization_to']
        )

        if organization.is_admin(self.user) is False:
            raise forms.ValidationError({
                'organization_to': 'Você não pode transferir um evento para'
                                   ' uma organização na qual você não é'
                                   ' administador.'
            })

        self.cleaned_data['organization_to'] = organization
        return self.cleaned_data

    def save(self):
        """ Salva dados em instância. """
        self.instance.organization = self.cleaned_data['organization_to']
        self.instance.place = None
        self.instance.save()
