from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import FormView

from gatheros_event.views.mixins import AccountMixin
from .forms import NewWorkForm


class WorkAddFormView(AccountMixin, FormView):
    template_name = "scientific_work/work_form.html"
    form_class = NewWorkForm
    success_url = reverse_lazy('front:start')

    def form_valid(self, form):
        messages.success(self.request, 'Submissão realizado com sucesso.')
        return super().form_valid(form)
