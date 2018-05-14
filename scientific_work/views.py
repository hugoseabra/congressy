from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import FormView

from gatheros_event.models import Event
from gatheros_event.views.mixins import AccountMixin
from .forms import NewWorkForm


class WorkAddFormView(AccountMixin, FormView):
    template_name = "scientific_work/work_form.html"
    form_class = NewWorkForm

    def get_login_url(self):
        return reverse_lazy('subscription:my-subscriptions')

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)

        event_pk = self.kwargs.get('event_pk')
        if not event_pk:
            messages.error(self.request, 'Não foi possivel resgatar o evento.')
            return redirect(reverse_lazy('front:start'))

        self.event = get_object_or_404(Event, pk=event_pk)

        return response

    def form_valid(self, form):
        messages.success(self.request, 'Submissão realizado com sucesso.')
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('scientific_work:work-add', kwargs={
            'event_pk': self.event.pk,
        })
