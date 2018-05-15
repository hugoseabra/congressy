from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import FormView

from gatheros_subscription.models import Subscription
from gatheros_event.views.mixins import AccountMixin
from .forms import NewWorkForm


class WorkAddFormView(AccountMixin, FormView):
    subscription = None
    template_name = "scientific_work/work_form.html"
    form_class = NewWorkForm

    def dispatch(self, request, *args, **kwargs):

        subscription_pk = self.kwargs.get('subscription_pk')
        if not subscription_pk:
            messages.error(self.request, 'Não foi possivel resgatar a '
                                         'inscrição.')
            return redirect(reverse_lazy('front:start'))

        self.subscription = get_object_or_404(Subscription, pk=subscription_pk)
        response = super().dispatch(request, *args, **kwargs)

        return response

    def form_valid(self, form):
        messages.success(self.request, 'Submissão realizado com sucesso.')
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

