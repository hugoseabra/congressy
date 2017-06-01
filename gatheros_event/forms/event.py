from django import forms
from gatheros_event.models import Event


class EventForm(forms.ModelForm):
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


class BaseEventPartialEdit(forms.ModelForm):
    def __init__(self, data=None, *args, **kwargs):
        super(BaseEventPartialEdit, self).__init__(data=data, *args, **kwargs)


class EventEditDatesForm(BaseEventPartialEdit):
    class Meta:
        model = Event
        fields = [
            'date_start',
            'date_end',
        ]


class EventEditSubscriptionTypeForm(BaseEventPartialEdit):
    class Meta:
        model = Event
        fields = [
            'subscription_type',
            'subscription_offline',
        ]


class EventPublicationForm(BaseEventPartialEdit):
    class Meta:
        model = Event
        fields = [
            'published',
        ]

    def clean_published(self):
        published = self.data['published']
        if type(published) == str:
            published = published == '1'

        return published
