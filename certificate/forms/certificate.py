from django import forms
from certificate.models import Certificate


class CertificatePartialForm(forms.ModelForm):

    class Meta:
        model = Certificate
        fields = [
            'event',
            'background_image',
            'text_content',
        ]

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


class CertificateForm(forms.ModelForm):
    """ Formulário de lote. """

    class Meta:
        """ Meta """
        model = Certificate
        fields = '__all__'
