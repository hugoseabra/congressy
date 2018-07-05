"""
Formulários de Informação de evento
"""
import base64
import binascii

from ckeditor.widgets import CKEditorWidget
from django import forms
from django.core.files.base import ContentFile

from core.forms.combined_form import CombinedFormBase
from gatheros_event.forms import PlaceForm
from gatheros_event.models import Info


class BaseModelFileForm(forms.ModelForm):
    """ Base de classe ModelForm para gerenciado de arquivos. """

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


class InfoForm(BaseModelFileForm):

    remove_image = forms.CharField(
        max_length=10,
        widget=forms.HiddenInput,
        required=False,
    )

    image_main = forms.CharField(
        widget=forms.HiddenInput,
        required=False,
    )

    class Meta:
        """ Meta """
        model = Info
        fields = [
            'lead',
            'description_html',
            'scientific_rules',
            'editorial_body',
            'voucher_extra_info',
        ]
        widgets = {
            'description_html': CKEditorWidget(),
            'scientific_rules': CKEditorWidget(),
            'editorial_body': CKEditorWidget(),
            'voucher_extra_info': forms.Textarea(attrs={
                'cols': '20', 'rows': '2'
            }),
            'image_main': forms.HiddenInput(),
        }

        help_texts = {
            'editorial_body': 'Corpo editorial que compõem sua organização',
            'scientific_rules': 'Normas do seu evento científico',
            'voucher_extra_info': 'Limite de 255 caracteres.'
        }
        labels = {
            'editorial_body': "Corpo editorial",
            'scientific_rules': "Normas do evento",
            'voucher_extra_info': "Informações extras para o voucher"
        }

    def __init__(self, event=None, **kwargs):
        self.event = event

        data = kwargs.get('data')

        if data:
            # TODO: this isn't DRY. Separate this logic into a helper.

            possible_remove_image = data.get('remove_image')
            possible_base64 = data.get('image_main')

            if possible_remove_image and possible_remove_image == 'True':

                data._mutable = True
                del data['image_main']
                data._mutable = False

                try:
                    event.info.image_main.delete(save=True)
                except AttributeError:
                    pass

            else:

                if possible_base64:
                    # Decoding from base64 avatar into a file obj.
                    try:
                        file_ext, imgstr = possible_base64.split(';base64,')
                        ext = file_ext.split('/')[-1]
                        file_name = str(event.slug) + "." + ext
                        data._mutable = True
                        data['image_main'] = ContentFile(
                            base64.b64decode(imgstr),
                            name=file_name
                        )
                        data._mutable = False
                    except (binascii.Error, ValueError):
                        pass

        super().__init__(**kwargs)

        if self.event.is_scientific:
            self.fields['description_html'].label = "Apresentação do evento"

        self.fields['image_main'].required = False

    def clean_event(self):
        return self.event

    # noinspection PyMethodMayBeStatic
    def clean_config_type(self):
        """ Limpa campo `config_type` """
        return Info.CONFIG_TYPE_MAIN_IMAGE

    def clear_image_main(self):
        """ Limpa campo `image4` """
        self._clear_file('image_main')
        return self.cleaned_data['image_main']

    def save(self, commit=True):
        self.instance.event = self.event
        image_main = self.data.get('image_main')
        if isinstance(image_main, ContentFile):
            self.instance.image_main = image_main
        return super().save(commit)


class HotsiteForm(CombinedFormBase):
    form_classes = {
        'info': InfoForm,
        'place': PlaceForm
    }
