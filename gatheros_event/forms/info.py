"""
Formulários de Informação de evento
"""

from django import forms

from gatheros_event.models import Info


# @TODO Remover diretórios vazios de eventos que não possuem banners

class BaseModelFileForm(forms.ModelForm):
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


class Info4ImagesForm(BaseModelFileForm):
    """Formulário de edição de 4 imagens pequenas"""

    class Meta:
        model = Info
        fields = [
            'image1',
            'image2',
            'image3',
            'image4',
            'text',
            'event',
            'config_type',
        ]
        widgets = {
            'event': forms.HiddenInput(),
            'config_type': forms.HiddenInput(),
        }

    # noinspection PyMethodMayBeStatic
    def clean_config_type(self):
        return Info.CONFIG_TYPE_4_IMAGES

    def clear_image1(self):
        self._clear_file('image1')
        return self.cleaned_data['image1']

    def clear_image2(self):
        self._clear_file('image2')
        return self.cleaned_data['image2']

    def clear_image3(self):
        self._clear_file('image3')
        return self.cleaned_data['image3']

    def clear_image4(self):
        self._clear_file('image4')
        return self.cleaned_data['image4']


class InfoMainImageForm(BaseModelFileForm):
    """Formulário de edição de 4 imagens pequenas"""

    class Meta:
        model = Info
        fields = [
            'image_main',
            'text',
            'event',
            'config_type',
        ]
        widgets = {
            'event': forms.HiddenInput(),
            'config_type': forms.HiddenInput(),
        }

    # noinspection PyMethodMayBeStatic
    def clean_config_type(self):
        return Info.CONFIG_TYPE_MAIN_IMAGE

    def clean_image_main(self):
        self._clear_file('image_main')
        return self.cleaned_data['image_main']


class InfoVideoForm(BaseModelFileForm):
    """Formulário de edição de 4 imagens pequenas"""

    class Meta:
        model = Info
        fields = [
            'youtube_video_id',
            'text',
            'event',
            'config_type',
        ]
        widgets = {
            'event': forms.HiddenInput(),
            'config_type': forms.HiddenInput(),
        }

    # noinspection PyMethodMayBeStatic
    def clean_config_type(self):
        return Info.CONFIG_TYPE_VIDEO
