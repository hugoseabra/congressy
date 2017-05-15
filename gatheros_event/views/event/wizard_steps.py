from django.forms import ModelForm, Widget, fields as form_fields
from django.shortcuts import get_list_or_404, get_object_or_404
from django.utils.safestring import mark_safe

from gatheros_event.models import Event, Place


class BaseAccountForm(object):
    organization = None
    user = None

    def populate_acount_data(self, initkwargs):
        for attr in ['user', 'organization']:
            if attr in initkwargs:
                setattr(self, attr, initkwargs[attr])
                del initkwargs[attr]

        return initkwargs


class EventFormBasicData(ModelForm, BaseAccountForm):
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
        kwargs = self.populate_acount_data(kwargs)
        super(EventFormBasicData, self).__init__(*args, **kwargs)

        self._create_organization_field()
        self._filter_place_field()

    def clean_organization(self):
        return self.organization

    def clean_place(self):
        place_pk = self.cleaned_data['place']

        if place_pk == 'add-place':
            EventFormPlaceNew.add_new_place = True
        elif place_pk:
            return get_object_or_404(Place, pk=place_pk)

    def _create_organization_field(self):
        organization = self.organization

        class OrganizationWidget(Widget):
            def render(self, name, value, attrs=None, renderer=None):
                return mark_safe(organization.name)

        self.fields['organization'] = form_fields.CharField(
            label='Realizador',
            widget=OrganizationWidget,
            required=False,
        )

    def _filter_place_field(self):
        places = get_list_or_404(Place, organization=self.organization)

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
            help_text="Se o evento for apenas on-line, deixe em branco.",
            initial=self.instance.place.pk if self.instance.place else None
        )


class EventFormPlaceNew(ModelForm, BaseAccountForm):
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
        kwargs = self.populate_acount_data(kwargs)
        super(EventFormPlaceNew, self).__init__(*args, **kwargs)
