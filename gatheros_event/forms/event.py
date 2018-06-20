"""
Formulários de Event
"""
import os
from datetime import datetime, timedelta

from django import forms
from django.shortcuts import get_object_or_404

from core.forms.widgets import SplitDateTimeBootsrapWidget
from gatheros_event.models import Event, Member, Organization
from gatheros_subscription.models import LotCategory


class DateTimeInput(forms.DateTimeInput):
    input_type = 'tel'


class EventForm(forms.ModelForm):
    """Formulário principal de evento"""

    class Meta:
        model = Event
        fields = [
            'organization',
            'category',
            'name',
            'date_start',
            'date_end',
            'has_optionals',
            'has_extra_activities',
            'has_checkin',
            'has_certificate',
            'has_survey',
            'event_type',
            'rsvp_type',
            'expected_subscriptions',
        ]

        widgets = {
            'organization': forms.HiddenInput,
            'event_type': forms.HiddenInput,
            'subscription_type': forms.RadioSelect,
            'date_start': SplitDateTimeBootsrapWidget,
            'date_end': SplitDateTimeBootsrapWidget,

        }

    def __init__(self, user, lang='pt-br', *args, **kwargs):
        self.user = user

        instance = kwargs.get('instance')

        super(EventForm, self).__init__(*args, **kwargs)
        # self.fields['is_scientific'].help_text = 'Trata-se de um evento com ' \
        #                                          'submissão de artigos ' \
        #                                          'cientificos?'

        if instance is None:
            self._configure_organization_field()

        self._hide_todo_config_fields()

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

    def clean_event_type(self):
        event_type = self.cleaned_data.get('event_type')
        self.instance.is_scientific = event_type == Event.EVENT_TYPE_SCIENTIFIC

        return event_type

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

    def save(self, commit=True):
        instance = super().save(commit)
        if instance.lot_categories.all().count() <= 0:
            general_category = LotCategory.objects.create(
                event=instance,
                name="Geral",
            )

            if instance.lots.all().count() == 1:
                first_lot = instance.lots.all().first()
                first_lot.category = general_category
                first_lot.save()

        return instance

    def _hide_todo_config_fields(self):
        todo_config_fields = (
            'has_optionals',
            'has_extra_activities',
            'has_checkin',
            'has_certificate',
        )
        if self.instance.pk is not None:
            for f_name in todo_config_fields:
                self[f_name].field.widget = forms.HiddenInput()


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
