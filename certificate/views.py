from django import forms as django_forms
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.http import HttpResponse
from django.shortcuts import reverse, redirect
from django.views import generic
from io import BytesIO
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from django.contrib import messages

from certificate import models, forms
from gatheros_event.views.mixins import EventViewMixin


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

        if self.event.certificate:
            form = forms.CertificatePartialForm(
                instance=self.event.certificate)
        else:
            form = super().get_form(form_class)
            form.initial['event'] = self.event.pk

        form.fields['event'].widget = django_forms.HiddenInput()
        return form

    def form_valid(self, form):
        self.instance = form.save()
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):

        if self.event.certificate:
            form = forms.CertificatePartialForm(
                instance=self.event.certificate, data=self.request.POST,
                files=self.request.FILES)
        else:
            form = forms.CertificatePartialForm(data=self.request.POST,
                                                files=self.request.FILES)

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


# class CertificatePDFView(AccountMixin, PDFTemplateView):
#     template_name = 'pdf/certificate.html'
#     subscription = None
#     event = None
#     person = None
#     lot = None
#     show_content_in_browser = False
#     permission_denied_url = reverse_lazy('front:start')
#
#     cmd_options = {
#         'margin-top': 5,
#         'javascript-delay': 500,
#     }
#
#     def get_filename(self):
#         return "CERTIFICADO--{}-{}.pdf".format(self.person.name,
#                                                self.event.name)
#
#     def pre_dispatch(self, request):
#         uuid = self.kwargs.get('pk')
#         self.subscription = get_object_or_404(Subscription,
#                                               uuid=uuid)
#         self.get_complementary_data()
#
#         return super().pre_dispatch(request)
#
#     def get_context_data(self, **kwargs):
#         context = super(CertificatePDFView, self).get_context_data(
#             **kwargs)
#
#         context['event'] = self.event
#         context['person'] = self.person
#         context['lot'] = self.lot
#         context['background_image'] = self.get_background_image()
#         context['organization'] = self.event.organization
#         context['subscription'] = self.subscription
#         return context
#
#     def get_complementary_data(self):
#         self.event = self.subscription.event
#         self.person = self.subscription.person
#         self.lot = self.subscription.lot
#
#     def get_background_image(self):
#         uri = staticfiles_storage.url('assets/img/certificate-example.jpg')
#         url = settings.BASE_DIR + "/frontend" + uri
#
#         with open(url, 'rb') as f:
#             read_data = f.read()
#             f.close()
#         return base64.b64encode(read_data)
#
#     def can_access(self):
#         return self.subscription.confirmed is True and \
#                self.subscription.attended is True


def certificate_pdf_view(request, event_pk, pk):
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="somefilename.pdf"'

    buffer = BytesIO()

    # Create the PDF object, using the BytesIO object as its "file."
    p = canvas.Canvas(buffer, pagesize=landscape(A4))

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    uri = staticfiles_storage.url('assets/img/certificate-example.jpg')
    url = settings.BASE_DIR + "/frontend" + uri

    p.drawImage(url, 0, 0, height=595, width=842, mask=None)
    p.drawString(x=300, y=100, text="Hello world.")

    # Close the PDF object cleanly.
    p.showPage()
    p.save()

    # Get the value of the BytesIO buffer and write it to the response.
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response
