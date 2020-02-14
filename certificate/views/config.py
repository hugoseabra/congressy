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
    ticket_name = "Lote 1 - Especial"
    cpf = "629.162.880-58"
    birth_date = "01/01/2012"
    category_name = "Categoria Estudantes"

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

        ref_object.text_content = ref_object.text_content.replace(
            "{{NOME}}",
            self.long_name
        )

        ref_object.text_content = ref_object.text_content.replace(
            "{{TICKET_NAME}}",
            self.ticket_name
        )

        ref_object.text_content = ref_object.text_content.replace(
            "{{CATEGORY_NAME}}",
            self.category_name
        )

        ref_object.text_content = ref_object.text_content.replace(
            "{{CPF}}",
            self.cpf
        )

        ref_object.text_content = ref_object.text_content.replace(
            "{{BIRTH_DATE}}",
            self.birth_date
        )

        ref_object.text_content = ref_object.text_content.replace(
            self.long_name,
            "<strong>" + self.long_name + "</strong>"
        )

        ref_object.text_content = ref_object.text_content.replace(
            self.ticket_name,
            "<strong>" + self.ticket_name + "</strong>"
        )

        ref_object.text_content = ref_object.text_content.replace(
            self.category_name,
            "<strong>" + self.category_name + "</strong>"
        )

        ref_object.text_content = ref_object.text_content.replace(
            self.cpf,
            "<strong>" + self.cpf + "</strong>"
        )

        ref_object.text_content = ref_object.text_content.replace(
            self.birth_date,
            "<strong>" + self.birth_date + "</strong>"
        )

        ref_object.text_content = ref_object.text_content.replace(
            "{{EVENTO}}",
            self.event.name
        )

        ref_object.text_content = ref_object.text_content.replace(
            self.event.name,
            "<strong>" + self.event.name + "</strong>"
        )

        if settings.DEBUG:
            base_path = os.path.join(
                settings.BASE_DIR,
                'frontend',
                'static',
            )
        else:
            base_path = settings.STATIC_ROOT

        premium_path = os.path.join(
            base_path,
            'assets',
            'img',
            'default_certificates',
            'premium',
            'default.jpg'
        )

        if os.path.exists(premium_path):
            with open(premium_path, 'rb') as f:
                premium = f.read()
                f.close()

            encoded_premium = b64encode(premium).decode("utf-8")
            context['premium_template_image'] = encoded_premium

        context['has_inside_bar'] = True
        context['active'] = 'certificate'
        context['object'] = ref_object
        context['has_city'] = self.object.event_has_city
        context['has_event_location'] = self.object.event_has_location

        context['form'] = forms.CertificatePartialForm(instance=self.object)
        return context
