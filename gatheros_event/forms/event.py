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
