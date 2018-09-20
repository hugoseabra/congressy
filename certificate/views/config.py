import os
from base64 import b64encode
from copy import copy

from django.conf import settings
from django.views import generic

from certificate import models, forms
from .mixins import CertificateFeatureFlagMixin


class CertificateConfigView(CertificateFeatureFlagMixin, generic.DetailView):
    template_name = 'certificate/certificado_.html'
    long_name = "Pedro de Alcântara João Carlos Leopoldo Salvador Bibiano"

    def get_object(self, queryset=None):

        obj, _ = models.Certificate.objects.get_or_create(
            event=self.event
        )

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if not isinstance(self.object, models.Certificate):
            self.object = self.get_object()

        ref_object = copy(self.object)
        # Objeto de referencia criado para não manipular o self.object que o
        # objeto de fato que é usado na instancia do form;

        ref_object.text_content = ref_object.text_content \
            .replace("{{NOME}}", self.long_name)

        ref_object.text_content = ref_object.text_content \
            .replace(self.long_name, "<strong>" + self.long_name + "</strong>")

        ref_object.text_content = ref_object.text_content \
            .replace("{{EVENTO}}", self.event.name)

        premium_path = os.path.join(
            settings.STATIC_ROOT,
            'assets',
            'img',
            'default_certificates',
            'premium',
            'default.jpg'
        )

        with open(premium_path, 'rb') as f:
            premium = f.read()
            f.close()

        encoded_premium = b64encode(premium).decode("utf-8")

        context['has_inside_bar'] = True
        context['active'] = 'certificate'
        context['premium_template_image'] = encoded_premium
        context['object'] = ref_object
        context['has_city'] = self.object.event_has_city
        context['has_event_location'] = self.object.event_has_location

        context['form'] = forms.CertificatePartialForm(instance=self.object)
        return context
