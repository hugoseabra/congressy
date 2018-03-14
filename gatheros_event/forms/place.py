from django import forms
from django.utils.safestring import mark_safe
from kanu_locations.models import City

from core.forms.cleaners import clear_string
from core.forms.widgets import AjaxChoiceField, TelephoneInput
from gatheros_event.models import Place


class GooglePictureWidget(forms.widgets.Widget):
    def render(self, name, value, **_):
        if not value:
            return ''

        link_attr = name.replace('img', 'link')
        link = getattr(value.instance, link_attr)
        return mark_safe(
            """
            <a target="_blank" href="{link}">
                <img src="{img}"></path>
            </a>
            """.format(link=link, img=value.url)
        )


FIELD_NAME_MAPPING = {
    'name': 'place_name',
}


class PlaceForm(forms.ModelForm):
    """ Formulário de local de evento. """

    states = (
        ('', '----'),
        # replace the value '----' with whatever you want, it won't matter
        ("AC", "AC"),
        ("AL", "AL"),
        ("AP", "AP"),
        ("AM", "AM"),
        ("BA", "BA"),
        ("CE", "CE"),
        ("DF", "DF"),
        ("ES", "ES"),
        ("GO", "GO"),
        ("MA", "MA"),
        ("MT", "MT"),
        ("MS", "MS"),
        ("MG", "MG"),
        ("PA", "PA"),
        ("PB", "PB"),
        ("PR", "PR"),
        ("PE", "PE"),
        ("PI", "PI"),
        ("RJ", "RJ"),
        ("RN", "RN"),
        ("RS", "RS"),
        ("RO", "RO"),
        ("RR", "RR"),
        ("SC", "SC"),
        ("SP", "SP"),
        ("SE", "SE"),
        ("TO", "TO"),
    )
    empty = (
        ('', '----'),
    )

    state = forms.ChoiceField(label='Estado', choices=states, required=False)
    city_name = AjaxChoiceField(label='Cidade', choices=empty, required=False)

    class Meta:
        """ Meta """
        model = Place
        fields = (
            'show_location',
            'lat',
            'long',
            'zoom',
            'show_address',
            'name',
            'phone',
            'zip_code',
            'street',
            'complement',
            'number',
            'village',
            'city',
            'reference',

        )

        widgets = {
            'city': forms.HiddenInput(),
            'zip_code': TelephoneInput(),
            'lat': forms.HiddenInput(),
            'long': forms.HiddenInput(),
            'zoom': forms.HiddenInput(),
        }

    def __init__(self, event, **kwargs):
        self.event = event
        super().__init__(**kwargs)

    def clean_city(self):
        city = self.cleaned_data.get('city')

        if city:
            city = City.objects.get(pk=self.data['city'])

        return city


    def save(self, commit=True):
        self.instance.event = self.event
        self.instance = super().save(commit=commit)
        return self.instance
