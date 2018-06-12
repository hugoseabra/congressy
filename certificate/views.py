from django import forms as django_forms
from django.shortcuts import reverse, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from django.template import Template, Context
from wkhtmltopdf.views import PDFTemplateView

from certificate import models, forms
from gatheros_event.views.mixins import EventViewMixin, AccountMixin
from gatheros_subscription.models import Subscription


class CertificateConfigView(EventViewMixin, generic.TemplateView):
    template_name = 'certificate/certificado_.html'
    object = None

    def dispatch(self, request, *args, **kwargs):
        response = super(CertificateConfigView, self).dispatch(request, *args,
                                                               **kwargs)
        self.object = models.Certificate.objects.get_or_create(
            event=self.event
        )

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if not self.object:
            self.object, _ = models.Certificate.objects.get_or_create(
                event=self.event
            )

        context['has_inside_bar'] = True
        context['active'] = 'certificate'
        context['object'] = self.object
        context['form'] = forms.CertificatePartialForm(instance=self.object)
        return context


class CertificateFormView(EventViewMixin, generic.FormView):
    template_name = 'certificate/certificate_form.html'
    model = models.Certificate
    slug_field = 'event__pk'
    slug_url_kwarg = 'event_pk'
    form_class = forms.CertificatePartialForm
    instance = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['has_inside_bar'] = True
        context['active'] = 'certificate'
        return context

    def get_success_url(self):
        return reverse('certificate:event-certificate-config', kwargs={
            'event_pk': self.event.pk,
        })

    def get_form(self, form_class=None):

        if not self.event.has_certificate:
            models.Certificate.objects.create(
                event=self.event
            )

        form = forms.CertificatePartialForm(
            instance=self.event.certificate)

        form.fields['event'].widget = django_forms.HiddenInput()
        return form

    def form_valid(self, form):
        self.instance = form.save()
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):

        form = forms.CertificatePartialForm(
            instance=self.event.certificate, data=self.request.POST,
            files=self.request.FILES)

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


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
        return context

    def get_complementary_data(self):
        self.event = self.subscription.event

    def get_text(self):
        text = self.event.certificate.text_content

        if "{{NOME}}" in text:
            text = text.replace("{{NOME}}", "<strong>{{NOME}}</strong>")

        text_template = Template(text)
        context = Context(
            {
                'NOME': self.subscription.person.name.upper(),
                'EVENTO': self.subscription.event.name,
                'CPF': self.subscription.person.cpf,
             }
        )
        res = text_template.render(context)
        return res

    def can_access(self):
        return self.subscription.confirmed is True and \
               self.subscription.attended is True

    def get_document_number(self):
        person = self.subscription.person

        if person.cpf:
            return person.cpf
        elif person.institution_cnpj:
            return person.institution_cnpj
        else:
            return ''
