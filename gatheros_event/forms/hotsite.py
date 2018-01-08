"""
Formulários de Informação de evento
"""
from ckeditor.widgets import CKEditorWidget
from django import forms

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


class HotsiteForm(BaseModelFileForm):
    class Meta:
        """ Meta """
        model = Info
        fields = [
            'image_main',
            'lead',
            'description_html',
        ]
        widgets = {
            'description_html': CKEditorWidget(),
        }

    def __init__(self, event, **kwargs):
        self.event = event
        super().__init__(**kwargs)

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
        return super().save(commit)
