"""
Formulários de Event
"""

from django import forms

from gatheros_event.models import Event


# @TODO Remover diretórios vazios de eventos que não possuem banners

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
        widgets = {'organization': forms.HiddenInput()}


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
