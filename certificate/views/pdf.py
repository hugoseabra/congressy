import base64
import json

import absoluteuri
import requests
from django.conf import settings
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template import Template, Context
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import generic

from gatheros_subscription.models import Subscription
from attendance.helpers.attendance import subscription_is_checked
from .mixins import CertificateFeatureFlagMixin


class CertificatePDFView(CertificateFeatureFlagMixin):
    template_name = 'pdf/certificate.html'
    subscription = None
    event = None
    permission_denied_url = reverse_lazy('front:start')
    wkhtml_ws_url = settings.WKHTMLTOPDF_WS_URL

    def get_filename(self):
        return "CERTIFICADO-{}-{}.pdf".format(
            self.subscription.pk,
            self.event.slug,
        )

    def create_html_string(self):
        return render_to_string(
            self.template_name,
            context=self.get_context_data()
        )

    def pre_dispatch(self, request):
        uuid = self.kwargs.get('pk')
        self.subscription = get_object_or_404(Subscription,
                                              uuid=uuid)
        self.get_complementary_data()

        return super().pre_dispatch(request)

    def get_context_data(self, **kwargs):
        context = {}

        if self.event.certificate.background_image:
            image_url = self.event.certificate.background_image.default.path

            with open(image_url, 'rb') as f:
                encoded_image = base64.b64encode(f.read()).decode()
            context['background_image'] = encoded_image

        bootstrap_path = static(
            'assets/plugins/bootstrap/css/bootstrap.min.css')
        main_css_path = static('assets/css/main.css')

        context['bootstrap_min_css'] = absoluteuri.build_absolute_uri(
            bootstrap_path
        )
        context['main_css'] = absoluteuri.build_absolute_uri(main_css_path)

        context['event'] = self.event
        context['certificate'] = self.event.certificate
        context['text'] = self.get_text()
        context['is_example'] = False
        return context

    def get_complementary_data(self):
        self.event = self.subscription.event

    def get_text(self):
        text = self.event.certificate.text_content
        text = text.replace("{{NOME}}", "<strong>{{NOME}}</strong>")

        text_template = Template(text)
        context = Context(
            {
                'NOME': self.subscription.person.name.upper(),
                'EVENTO': self.subscription.event.name,
            }
        )
        res = text_template.render(context)
        return res

    def can_access(self):

        if not self.subscription.confirmed:
            return False

        certificate_config = self.subscription.event.certificate
        
        if certificate_config.only_attending_participantes:

            if not subscription_is_checked(self.subscription.pk):

                self.permission_denied_message = "Certificado disponivel " \
                                                 "apenas participantes com " \
                                                 "presença confirmada!"
                return False

        return True

    def get(self, request, *args, **kwargs):
        html = self.create_html_string()
        encoded = base64.b64encode(html.encode()).decode()

        data = {
            'contents': encoded,
            'options': {
                'dpi': '96',
                'margin-top': '0',
                'margin-left': '0',
                'margin-right': '0',
                'margin-bottom': '0',
                'page-size': 'A4',
                'orientation': 'Landscape',
            },
        }

        headers = {
            'Content-Type': 'application/json',  # This is important
        }

        response = requests.post(
            self.wkhtml_ws_url,
            data=json.dumps(data),
            headers=headers,
        )

        if response.status_code != 200:
            raise Exception('Could not create PDF')

        pdf = ContentFile(response.content, name=self.get_filename())
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="{}"'.format(
            self.get_filename()
        )

        return response


class CertificatePDFExampleView(CertificateFeatureFlagMixin):
    template_name = 'pdf/certificate.html'
    event = None
    long_name = "Pedro de Alcântara João Carlos Leopoldo Salvador Bibiano"
    wkhtml_ws_url = settings.WKHTMLTOPDF_WS_URL

    def get_filename(self):
        return "CERTIFICADO-SAMPLE-{}.pdf".format(self.event.slug)

    def create_html_string(self):
        return render_to_string(
            self.template_name,
            context=self.get_context_data()
        )

    def get_context_data(self):
        context = {}

        if self.event.certificate.background_image:
            image_url = self.event.certificate.background_image.default.path

            with open(image_url, 'rb') as f:
                encoded_image = base64.b64encode(f.read()).decode()
            context['background_image'] = encoded_image

        bootstrap_path = \
            static('assets/plugins/bootstrap/css/bootstrap.min.css')
        main_css_path = static('assets/css/main.css')

        context['bootstrap_min_css'] = absoluteuri.build_absolute_uri(
            bootstrap_path
        )
        context['main_css'] = absoluteuri.build_absolute_uri(main_css_path)

        context['certificate'] = self.event.certificate
        context['text'] = self.get_text()
        return context

    def get_text(self):
        text = self.event.certificate.text_content

        text = text.replace("{{NOME}}", "<strong>{{NOME}}</strong>")

        text_template = Template(text)
        context = Context(
            {
                'NOME': self.long_name,
                'EVENTO': self.event.name,
                'CPF': "629.162.880-58",
            }
        )

        return text_template.render(context)

    def get(self, request, *args, **kwargs):
        html = self.create_html_string()
        encoded = base64.b64encode(html.encode()).decode()

        data = {
            'contents': encoded,
            'options': {
                'dpi': '96',
                'margin-top': '0',
                'margin-left': '0',
                'margin-right': '0',
                'margin-bottom': '0',
                'page-size': 'A4',
                'orientation': 'Landscape',
            },
        }

        headers = {
            'Content-Type': 'application/json',  # This is important
        }

        response = requests.post(
            self.wkhtml_ws_url,
            data=json.dumps(data),
            headers=headers,
        )

        if response.status_code != 200:
            raise Exception('Could not create PDF')

        pdf = ContentFile(response.content, name=self.get_filename())
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="{}"'.format(
            self.get_filename()
        )

        return response


class CertificateManualView(CertificateFeatureFlagMixin,
                            generic.TemplateView):
    template_name = 'certificate/manual.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['has_inside_bar'] = True
        context['active'] = 'certificate-manual'
        context['certificate'] = self.event.certificate
        return context
