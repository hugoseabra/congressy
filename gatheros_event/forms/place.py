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
        ("AC", "Acre"),
        ("AL", "Alagoas"),
        ("AP", "Amapá"),
        ("AM", "Manaus"),
        ("BA", "Bahia"),
        ("CE", "Ceará"),
        ("DF", "Distrito Federal"),
        ("ES", "Espírito Santo"),
        ("GO", "Goiás"),
        ("MA", "Maranhão"),
        ("MT", "Mato Grosso"),
        ("MS", "Mato Grosso do Sul"),
        ("MG", "Minas Gerais"),
        ("PA", "Pará"),
        ("PB", "Paraíba"),
        ("PR", "Paraná"),
        ("PE", "Pernambuco"),
        ("PI", "Piauí"),
        ("RJ", "Rio de Janeiro"),
        ("RN", "Rio Grande do Norte"),
        ("RS", "Rio Grande do Sul"),
        ("RO", "Rondônia"),
        ("RR", "Roraima"),
        ("SC", "Santa Catarina"),
        ("SP", "São Paulo"),
        ("SE", "Sergipe"),
        ("TO", "Tocantins"),
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
        }

    def __init__(self, event, **kwargs):
        self.event = event
        super().__init__(**kwargs)

    def clean_city(self):
        if 'city' not in self.data:
            return None

        return City.objects.get(pk=self.data['city'])

    def save(self, commit=True):
        self.instance.event = self.event
        self.instance = super().save(commit=commit)
        return self.instance
