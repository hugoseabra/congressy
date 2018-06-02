from django import forms as django_forms
from django.contrib import messages
from django.shortcuts import reverse, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from django.template import Template
from wkhtmltopdf.views import PDFTemplateView

from certificate import models, forms
from gatheros_event.views.mixins import EventViewMixin, AccountMixin
from gatheros_subscription.models import Subscription


class CertificateConfigView(EventViewMixin, generic.DetailView):
    template_name = 'certificate/certificado_.html'
    model = models.Certificate

    def dispatch(self, request, *args, **kwargs):
        response = super(CertificateConfigView, self).dispatch(request, *args,
                                                               **kwargs)
        if not self.object.background_image:
            messages.error(request, 'Seu certificado não possui uma imagem '
                                    'de fundo.')
            return redirect('certificate:event-certificate-prepare',
                            event_pk=self.event.pk)

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['has_inside_bar'] = True
        context['active'] = 'certificate'
        return context


class CertificatePrepareView(EventViewMixin, generic.FormView):
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
            'pk': self.instance.pk
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
    show_content_in_browser = False
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
        context['certificate'] = self.event.certificate
        context['text'] = self.get_text()
        return context

    def get_complementary_data(self):
        self.event = self.subscription.event

    def get_text(self):
        text = self.event.certificate.text_content
        text_template = Template(text)
        res = text_template.render(NOME=self.subscription.person.name.upper())
        return res

    def can_access(self):
        return self.subscription.confirmed is True and \
               self.subscription.attended is True

# def certificate_pdf_view(request, event_pk, pk):
#     # Create the HttpResponse object with the appropriate PDF headers.
#     response = HttpResponse(content_type='application/pdf')
#
#     event = get_object_or_404(Event, pk=event_pk)
#     subscription = get_object_or_404(Subscription, pk=pk)
#
#     if subscription.status != Subscription.CONFIRMED_STATUS or not \
#             subscription.attended:
#         return HttpResponse(status=404)
#
#     try:
#         certificate = event.certificate
#     except models.Certificate.DoesNotExist:
#         return HttpResponse(status=400)
#
#     if not certificate.background_image:
#         return HttpResponse(status=400)
#
#     file_name = '{}-{}.pdf'.format(event.name, subscription.person.name)
#     response[
#         'Content-Disposition'] = 'attachment; filename="' + file_name + '"'
#
#     buffer = BytesIO()
#
#     # Create the PDF object, using the BytesIO object as its "file."
#     p = canvas.Canvas(buffer, pagesize=landscape(A4))
#
#     # Draw things on the PDF. Here's where the PDF generation happens.
#     # See the ReportLab documentation for the full list of functionality.
#     image_path = certificate.background_image.path
#
#     p.drawImage(image_path, 0, 0, height=595, width=842)
#     if not certificate.title_hide and event.certificate.title_content:
#         p.setFont("Helvetica", event.certificate.title_font_size)
#         x_coordinate = event.certificate.title_position_x
#         y_coordinate = event.certificate.title_position_y
#         title = event.certificate.title_content
#         p.drawString(x=x_coordinate, y=y_coordinate, text=title)
#
#     if certificate.text_content:
#         p.setFont("Helvetica", event.certificate.text_font_size)
#         x_coordinate = event.certificate.text_position_x
#         y_coordinate = event.certificate.text_position_y
#         text = event.certificate.text_content
#         text_template = Template(text)
#         res = text_template.render(nome=subscription.person.name)
#         p.drawString(x=x_coordinate, y=y_coordinate, text=res)
#
#     if not certificate.date_hide and certificate.date_content:
#         p.setFont("Helvetica", certificate.date_font_size)
#         x_coordinate = certificate.date_position_x
#         y_coordinate = certificate.date_position_y
#         date = certificate.date_content
#         p.drawString(x=x_coordinate, y=y_coordinate, text=date)
#
#     # Close the PDF object cleanly.
#     p.showPage()
#     p.save()
#
#     # Get the value of the BytesIO buffer and write it to the response.
#     pdf = buffer.getvalue()
#     buffer.close()
#     response.write(pdf)
#     return response
