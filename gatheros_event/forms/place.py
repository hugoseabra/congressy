import re
from io import BytesIO
from urllib.parse import urlencode

import requests
from django import forms
from django.conf import settings
from django.core.files import File
from django.utils.safestring import mark_safe

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

    class Meta:
        """ Meta """
        model = Place
        fields = (
            'show_location',
            'lat',
            'long',
            # 'show_address',
            # 'name',
            # 'phone',
            # 'zip_code',
            # 'street',
            # 'complement',
            # 'number',
            # 'village',
            # 'city',
            # 'reference',

        )
        widgets = {
            'organization': forms.HiddenInput(),
            'google_maps_img': GooglePictureWidget(),
            'google_streetview_img': GooglePictureWidget(),
        }

    def __init__(self, event=None, **kwargs):
        self.event = event
        super().__init__(**kwargs)

    # def add_prefix(self, field_name):
    #     # look up field name; return original if not found
    #     field_name = FIELD_NAME_MAPPING.get(field_name, field_name)
    #     return super().add_prefix(field_name)

    def clean_google_streetview_link(self):
        """ Validando o link do Google StreetViuew """
        if not self.cleaned_data['google_streetview_link']:
            return None

        return self.cleaned_data['google_streetview_link']

    def _get_streetview_parans(self):
        url = self.cleaned_data['google_streetview_link']
        if not url:
            return None

        assert 'google.com' in self.cleaned_data['google_streetview_link']
        assert '/maps/' in self.cleaned_data['google_streetview_link']

        parsed = re.compile(r'/@(.*),(.+),(.+),(.+),(.+),(.+)/').search(url)
        return {
            'latitude': float(parsed.group(1)),
            'longitude': float(parsed.group(2)),
            'heading': float(parsed.group(5).replace('h', '')),
            'pitch': int(float(parsed.group(6).replace('t', ''))) - 90,
            'fov': int(float(parsed.group(4).replace('y', '')))
        }

    def clean_google_maps_link(self):
        """
        Construindo a url do Google Maps pela url do Google StreetView
        :return: str
        """
        params = self._get_streetview_parans()

        if not params:
            return None

        query = {
            'api': 1,
            'z': 10,
            'query': '%s,%s' % (params['latitude'], params['longitude'])
        }
        base_url = 'https://www.google.com/maps/search/?'
        return base_url + urlencode(query, True)

    def clean_google_maps_img(self):
        """
        Fazendo o download da imagem estática do Google Maps
        :return: Img
        """

        params = self._get_streetview_parans()

        if not params:
            return None

        center = '%s,%s' % (params['latitude'], params['longitude'])
        query = {
            'maptype': 'roadmap',
            'size': '640x480',
            'center': center,
            'zoom': 14,
            'key': settings.GOOGLE_MAPS_API_KEY,
            'markers': 'color:red|%s' % center
        }
        base_url = 'https://maps.googleapis.com/maps/api/staticmap?'
        url = base_url + urlencode(query, True)

        # Download da imagem
        res = requests.get(url)
        file_name = '%s,%s,maps.png' % (params['latitude'],
                                        params['longitude'])
        return File(BytesIO(res.content), file_name)

    def clean_google_streetview_img(self):
        """
        Fazendo o download da imagem estática do Google StreetView
        :return: Img
        """

        params = self._get_streetview_parans()

        if not params:
            return None

        query = {
            'size': '640x480',
            'heading': params['heading'],
            'pitch': params['pitch'],
            'fov': params['fov'],
            'location': '%s,%s' % (params['latitude'], params['longitude']),
            'key': settings.GOOGLE_MAPS_API_KEY,
        }
        base_url = 'https://maps.googleapis.com/maps/api/streetview?'
        url = base_url + urlencode(query, True)

        # Download da imagem
        res = requests.get(url)
        file_name = '%s,%s,streetview.png' % (params['latitude'],
                                              params['longitude'])
        return File(BytesIO(res.content), file_name)

    def save(self, commit=True):
        self.instance.event = self.event
        return super().save(commit)
