from django.forms import ModelForm, Widget, fields as form_fields
from django.shortcuts import get_object_or_404, get_list_or_404
from django.utils.safestring import mark_safe

from core.view.user_context import UserContextFormMixin
from gatheros_event.models import Event, Organization, Place


class EventFormBasicData(UserContextFormMixin, ModelForm):
    organization = None

    class Meta:
        model = Event
        fields = [
            'organization',
            'category',
            'name',
            'date_start',
            'date_end',
            'place',
            'description',
            'subscription_type',
            'subscription_offline',
        ]

    def __init__(self, *args, **kwargs):
        super(EventFormBasicData, self).__init__(*args, **kwargs)
        self.organization = self.user_context.active_organization
        self._create_organization_field()
        self._filter_place_field()
        self._set_initial_data()

    def _set_initial_data(self):
        self.fields['category'].initial = 2
        self.fields['name'].initial = 'Event Teste'
        self.fields['date_start'].initial = '2017-05-25 08:00'
        self.fields['date_end'].initial = '2017-05-25 18:00'
        self.fields['description'].initial = 'Descrição qualquer'

    def clean_organization(self):
        return get_object_or_404(Organization, pk=self.organization.pk)

    def clean_place(self):
        place_pk = self.cleaned_data['place']

        if place_pk == 'add-place':
            EventFormPlaceNew.add_new_place = True
        elif place_pk:
            return get_object_or_404(Place, pk=place_pk)

    def _create_organization_field(self):
        organization = self.user_context.active_organization

        class OrganizationWidget(Widget):
            def render(self, name, value, attrs=None, renderer=None):
                return mark_safe(organization.name)

        self.fields['organization'] = form_fields.CharField(
            label='Realizador',
            widget=OrganizationWidget,
            required=False,
        )

    def _filter_place_field(self):

        organization = self.user_context.active_organization
        places = get_list_or_404(Place, organization__pk=organization.pk)

        if self.instance.pk:
            place_choices = ([(place.pk, place.name) for place in places])
        else:
            place_choices = (
                (None, '---------'),
                ('add-place', 'Cadastrar novo local'),
                ('Meus locais', [(place.pk, place.name) for place in places]),
            )

        self.fields['place'] = form_fields.ChoiceField(
            label='Local',
            choices=place_choices,
            required=False,
            help_text="Se o evento for apenas on-line, deixe em branco."
        )


class EventFormPlaceNew(UserContextFormMixin, ModelForm):
    organization = None
    add_new_place = False
    template_name = 'gatheros_event/event/wizard/steps/place.html'

    class Meta:
        model = Place
        fields = [
            'name',
            'phone',
            'zip_code',
            'city',
            'street',
            'number',
            'complement',
            'village',
            'reference',
            'organization',
        ]
        widgets = {
            'organization': form_fields.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        super(EventFormPlaceNew, self).__init__(*args, **kwargs)
        self.organization = self.user_context.active_organization
        self._set_initial_data()

    def _set_initial_data(self):
        self.fields['organization'].initial = self.organization.pk

        self.fields['name'].initial = 'Um lugar qualquer'
        self.fields['phone'].initial = '9855258'
        self.fields['zip_code'].initial = '75400000'
        self.fields['city'].initial = 5413
        self.fields['street'].initial = 'Rua dos bobos'
        self.fields['number'].initial = '010'
        self.fields['complement'].initial = 'Qd. 00, Lt. 100'
        self.fields['village'].initial = 'Bairro Feliz'
        self.fields['reference'].initial = 'Próximo da rua das crianças'
