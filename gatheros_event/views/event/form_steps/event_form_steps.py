from django.forms import ModelForm, Widget, fields
from django.utils.safestring import mark_safe

from core.view.user_context import UserContextFormMixin
from gatheros_event.models import Event, Place


class EventFormStep1(UserContextFormMixin, ModelForm):
    class Meta:
        model = Event
        fields = [
            'organization',
            'category',
            'name',
            'description',
            'date_start',
            'date_end',
            'place',
        ]

    def __init__( self, *args, **kwargs ):
        super(EventFormStep1, self).__init__(*args, **kwargs)
        self._create_organization_field()
        self._filter_place_field()

    def _create_organization_field( self ):
        if self.user_context.get('superuser', False) is True:
            return

        organizations = self.user_context.get('organizations', [])
        organizations = [
            (org.get('pk'), org.get('name')) for org in organizations if org
        ]

        active_organization = self.user_context.get('active_organization')

        self.fields['organization'] = fields.ChoiceField(
            choices=organizations,
            initial=active_organization.get('pk'),
            required=True,
        )

    def _filter_place_field( self ):
        active_organization = self.user_context.get('active_organization')

        places = Place.objects.filter(
            organization__pk=active_organization.get('pk')
        ).order_by('name')
        initial_place = places.first()

        place_choices = (
            ('Novo local', (
                (None, 'Cadastrar local'),
            )),
            ('Meus locais', (
                [(place.pk, place.name) for place in places]
            )),
        )

        self.fields['place'] = fields.ChoiceField(
            label='Local',
            choices=place_choices,
            initial=initial_place.pk,
            required=True,
        )

        class Address(Widget):
            def render( self, value, **kwargs ):
                return mark_safe(value) if value is not None else ''

        self.fields['address'] = fields.CharField(
            label='Endereço',
            widget=Address,
            initial=initial_place.get_complete_address()
        )


class EventFormStep2(UserContextFormMixin, ModelForm):
    class Meta:
        model = Event
        fields = [
            'subscription_type',
            'subscription_offline',
        ]


class EventFormStep3(UserContextFormMixin, ModelForm):
    class Meta:
        model = Event
        fields = [
            'banner_top',
            'banner_small',
            'banner_slide',
            'banner_slide',
        ]


class EventFormStep4(UserContextFormMixin, ModelForm):
    class Meta:
        model = Event
        fields = [
            'website',
            'facebook',
            'twitter',
            'linkedin',
            'skype',
        ]
