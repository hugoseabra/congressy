from django import forms

from certificate.models import Certificate
from core.forms.widgets import ColorInput
from gatheros_event.models import Event


class CertificatePartialForm(forms.ModelForm):
    event = None

    class Meta:
        model = Certificate
        fields = [
            'event',
            'background_image',
            'text_content',
            'event_location',
            'only_attending_participantes',
            'font_color',
        ]

        widgets = {
            'event': forms.HiddenInput(),
            'font_color': ColorInput(),
        }

        help_texts = {
            'font_color': 'Cor da fonte do seu certificado em formato '
                          'hexdecimal.'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Esse get está fora do bloco de try por que se não achar, é pra dar
        # pau mesmo.
        self.event = Event.objects.get(pk=self.initial.get('event'))

        if hasattr(self.event, 'place'):
            place = self.event.place

            if place and hasattr(place, 'city') and place.city:
                self.initial['event_location'] = place.city.name.title()
                self.fields['event_location'].disabled = True

    def clear_background_image(self):
        """ Limpa campo `image4` """
        self._clear_file('background_image')
        return self.cleaned_data['background_image']

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

    def clean_text_content(self):
        text_content = self.cleaned_data['text_content']
        text_content = text_content.strip()
        text_content = text_content \
            .replace('\r\n', ' ') \
            .replace('\r', ' ') \
            .replace('\n', ' ') \
            .replace('{{ ', '{{') \
            .replace(' }}', '}}')

        return text_content


class CertificateForm(forms.ModelForm):
    """ Formulário de lote. """

    class Meta:
        """ Meta """
        model = Certificate
        fields = '__all__'
