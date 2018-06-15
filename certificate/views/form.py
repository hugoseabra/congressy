from django import forms as django_forms
from django.shortcuts import reverse
from django.views import generic

from certificate import models, forms
from gatheros_event.views.mixins import EventViewMixin


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

        if not self.event.has_certificate_config:
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
