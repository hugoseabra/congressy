"""
Formulários de Event
"""

from django import forms

from gatheros_event.models import Event


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
            'description',
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
        if self.data.get('banner_small-clear'):
            self._clear_file('banner_small')

        return self.cleaned_data['banner_small']

    def clean_banner_top(self):
        if self.data.get('banner_top-clear'):
            self._clear_file('banner_top')

        return self.cleaned_data['banner_top']

    def clean_banner_slide(self):
        if self.data.get('banner_slide-clear'):
            self._clear_file('banner_slide')

        return self.cleaned_data['banner_slide']

    def _clear_file(self, field_name):
        """Removes files from model"""
        file = getattr(self.instance, field_name)
        storage = file.storage
        path = file.path
        storage.delete(path)
