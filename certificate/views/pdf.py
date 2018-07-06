from django.shortcuts import get_object_or_404
from django.template import Template, Context
from django.urls import reverse_lazy
from django.views import generic
from wkhtmltopdf.views import PDFTemplateView

from gatheros_event.models import Event
from gatheros_event.views.mixins import AccountMixin, EventViewMixin
from gatheros_subscription.models import Subscription


class CertificatePDFView(AccountMixin, PDFTemplateView):
    template_name = 'pdf/certificate.html'
    subscription = None
    event = None
    show_content_in_browser = True
    permission_denied_url = reverse_lazy('front:start')

    cmd_options = {
        'dpi': 96,
        'margin-top': 0,
        'margin-bottom': 0,
        'margin-left': 0,
        'margin-right': 0,
        'page-size': 'A4',
        'orientation': 'Landscape',
    }

    def get_filename(self):
        return "CERTIFICADO--{}-{}.pdf".format(self.subscription.person.name,
                                               self.event.name)

    def pre_dispatch(self, request):
        uuid = self.kwargs.get('pk')
        self.subscription = get_object_or_404(Subscription,
                                              uuid=uuid)
        self.get_complementary_data()

        return super().pre_dispatch(request)

    def get_context_data(self, **kwargs):
        context = super(CertificatePDFView, self).get_context_data(**kwargs)
        image_url = self.event.certificate.background_image.default.url
        context['background_image'] = image_url
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
        return self.subscription.confirmed is True and \
               self.subscription.attended is True


class CertificatePDFExampleView(AccountMixin, PDFTemplateView):
    template_name = 'pdf/certificate.html'
    event = None
    show_content_in_browser = True
    permission_denied_url = reverse_lazy('front:start')
    long_name = "Pedro de Alcântara João Carlos Leopoldo Salvador Bibiano"

    cmd_options = {
        'dpi': 96,
        'margin-top': 0,
        'margin-bottom': 0,
        'margin-left': 0,
        'margin-right': 0,
        'page-size': 'A4',
        'orientation': 'Landscape',
    }

    def pre_dispatch(self, request):
        event_pk = self.kwargs.get('event_pk')
        self.event = get_object_or_404(Event, pk=event_pk)
        return super().pre_dispatch(request)

    def get_context_data(self, **kwargs):
        context = super(CertificatePDFExampleView, self).get_context_data(
            **kwargs)

        if self.event.certificate.background_image:
            image_url = self.event.certificate.background_image.default.url
            context['background_image'] = image_url

        context['event'] = self.event
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


class CertificateManualView(EventViewMixin, generic.TemplateView):
    template_name = 'certificate/manual.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['has_inside_bar'] = True
        context['active'] = 'certificate-manual'
        return context
