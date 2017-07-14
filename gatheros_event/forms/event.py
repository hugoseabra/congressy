"""
Formulários de Event
"""

from django import forms
from django.shortcuts import get_object_or_404

from gatheros_event.models import Event, Member, Organization


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
            'subscription_type',
            'subscription_offline',
            'published'
        ]
        widgets = {'organization': forms.HiddenInput}

    def __init__(self, user, *args, **kwargs):
        self.user = user

        super(EventForm, self).__init__(*args, **kwargs)

        instance = kwargs.get('instance')
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
        self._clear_file('banner_small')
        return self.cleaned_data['banner_small']

    def clean_banner_top(self):
        self._clear_file('banner_top')
        return self.cleaned_data['banner_top']

    def clean_banner_slide(self):
        self._clear_file('banner_slide')
        return self.cleaned_data['banner_slide']

    def _clear_file(self, field_name):
        """Removes files from model"""

        if field_name not in self.changed_data:
            return

        file = getattr(self.instance, field_name)
        if not file:
            return

        storage = file.storage
        path = file.path
        storage.delete(path)

        storage = file.default.storage
        path = file.default.path
        storage.delete(path)

        storage = file.thumbnail.storage
        path = file.thumbnail.path
        storage.delete(path)


class EventPlaceForm(forms.ModelForm):
    """Formulário de edição de local de evento."""

    class Meta:
        model = Event
        fields = [
            'place',
        ]

    def __init__(self, *args, **kwargs):
        super(EventPlaceForm, self).__init__(*args, **kwargs)
        self._filter_places()

    def _filter_places(self):
        organization = self.instance.organization
        place_qs = organization.places

        self.fields['place'].widget = forms.Select(
            attrs={'onclick': 'submit()'},
            choices=place_qs.all()
        )
        self.fields['place'].queryset = place_qs.all()


class EventSocialMediaForm(forms.ModelForm):
    """Formulário de edição de local de evento."""

    class Meta:
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
        self.instance.organization = self.cleaned_data['organization_to']
        self.instance.place = None
        self.instance.save()
