from django.shortcuts import render

from gatheros_event.views.mixins import AccountMixin
from django.views import generic

from gatheros_event.models import Event
from certificate import models


class CertificadoView(AccountMixin, generic.DetailView):
    template_name = 'certificate/certificado_.html'
    model = models.Certificate
    slug_field = 'event__pk'
    slug_url_kwarg = 'event_pk'
