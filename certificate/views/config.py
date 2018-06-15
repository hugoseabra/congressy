from copy import copy

from django.views import generic

from certificate import models, forms
from gatheros_event.views.mixins import EventViewMixin


class CertificateConfigView(EventViewMixin, generic.TemplateView):
    template_name = 'certificate/certificado_.html'
    object = None
    long_name = "Pedro de Alcântara João Carlos Leopoldo Salvador Bibiano"

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

        ref_object = copy(self.object)
        # Objeto de referencia criado para não manipular o self.object que o
        # objeto de fato que é usado na instancia do form;

        ref_object.text_content = ref_object.text_content \
            .replace("{{NOME}}", self.long_name)

        ref_object.text_content = ref_object.text_content \
            .replace(self.long_name, "<strong>" + self.long_name + "</strong>")

        ref_object.text_content = ref_object.text_content \
            .replace("{{EVENTO}}", self.event.name)

        context['has_inside_bar'] = True
        context['active'] = 'certificate'
        context['object'] = ref_object

        context['form'] = forms.CertificatePartialForm(instance=self.object)
        return context
