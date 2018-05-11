from django.views.generic import FormView
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import NewWorkForm


class WorkAddFormView(FormView):
    template_name = "scientific_work/work_form.html"
    form_class = NewWorkForm
    success_url = reverse_lazy('scientific_work:work-add')

    def form_valid(self, form):
        messages.success(self.request, 'Submissão realizado com sucesso.')
        return super().form_valid(form)
