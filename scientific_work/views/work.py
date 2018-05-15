from django.contrib import messages
from django.urls import reverse_lazy
from django.views import generic

from scientific_work.forms import NewWorkForm
from .mixins import WorkViewMixin
from scientific_work.models import Work


class WorkAddView(WorkViewMixin, generic.FormView):
    template_name = "scientific_work/form.html"
    form_class = NewWorkForm

    def form_valid(self, form):
        messages.success(self.request, 'Submissão criada com sucesso.')
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('scientific_work:work-list', kwargs={
            'subscription_pk': self.subscription.pk,
        })

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['subscription'] = self.subscription
        return kwargs


class WorkListView(WorkViewMixin, generic.ListView):
    template_name = "scientific_work/list.html"

    def get_queryset(self):
        return Work.objects.filter(subscription=self.subscription)