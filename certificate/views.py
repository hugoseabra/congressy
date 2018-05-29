from django.views import generic

from certificate import models
from gatheros_event.views.mixins import EventViewMixin


class CertificadoView(EventViewMixin, generic.DetailView):
    template_name = 'certificate/certificado_.html'
    model = models.Certificate

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['has_inside_bar'] = True
        context['active'] = 'certificate'
        return context
