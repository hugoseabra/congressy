from django.contrib import messages
from django.urls import reverse_lazy
from django.views import generic

from scientific_work.forms import NewWorkForm
from scientific_work.models import Work
from .helpers import is_ready
from .mixins import WorkViewMixin, EventViewMixin


class WorkAddView(WorkViewMixin, generic.FormView):
    template_name = "scientific_work/form.html"
    form_class = NewWorkForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active'] = 'scientific_work'
        context['has_inside_bar'] = True
        context['event'] = self.subscription.event
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Submissão criada com sucesso.')
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('scientific_work:work-config-list', kwargs={
            'subscription_pk': self.subscription.pk,
        })

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['subscription'] = self.subscription
        return kwargs


class WorkConfigListView(WorkViewMixin, generic.ListView):
    template_name = "scientific_work/config-list.html"

    def get_queryset(self):
        return Work.objects.filter(subscription=self.subscription)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        work_list = context['object_list']
        work_list_with_status = []
        for work in work_list:
            work.ready = is_ready(work)

            work_list_with_status.append(work)

        context['object_list'] = list(self.chunks(work_list_with_status, 2))
        context['subscription'] = self.subscription

        return context

    @staticmethod
    def chunks(l, n):
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(l), n):
            yield l[i:i + n]


class WorkListView(EventViewMixin, generic.ListView):
    template_name = "scientific_work/list.html"

    def get_queryset(self):
        return Work.objects.filter(subscription__event=self.event)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        work_list = context['object_list']
        work_list_with_status = []
        for work in work_list:
            work.ready = is_ready(work)

            work_list_with_status.append(work)

        context['object_list'] = work_list_with_status
        context['active'] = 'scientific_work'
        context['has_inside_bar'] = True
        context['event'] = self.event

        return context
