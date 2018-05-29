from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from wkhtmltopdf.views import PDFTemplateView

from certificate import models
from gatheros_event.views.mixins import AccountMixin
from gatheros_subscription.models import Subscription


class CertificadoView(AccountMixin, generic.DetailView):
    template_name = 'certificate/certificado_.html'
    model = models.Certificate
    slug_field = 'event__pk'
    slug_url_kwarg = 'event_pk'


class CertificatePDFView(AccountMixin, PDFTemplateView):
    template_name = 'pdf/certificate.html'
    subscription = None
    event = None
    person = None
    lot = None
    show_content_in_browser = False
    permission_denied_url = reverse_lazy('front:start')

    cmd_options = {
        'margin-top': 5,
        'javascript-delay': 500,
    }

    def get_filename(self):
        return "CERTIFICADO--{}-{}.pdf".format(self.person.name,
                                               self.event.name)

    def pre_dispatch(self, request):
        uuid = self.kwargs.get('pk')
        self.subscription = get_object_or_404(Subscription,
                                              uuid=uuid)
        self.get_complementary_data()

        return super().pre_dispatch(request)

    def get_context_data(self, **kwargs):
        context = super(CertificatePDFView, self).get_context_data(
            **kwargs)

        context['event'] = self.event
        context['person'] = self.person
        context['lot'] = self.lot
        context['organization'] = self.event.organization
        context['subscription'] = self.subscription
        return context

    def get_complementary_data(self):
        self.event = self.subscription.event
        self.person = self.subscription.person
        self.lot = self.subscription.lot

    def can_access(self):
        return self.subscription.confirmed is True and \
               self.subscription.attended is True
