from django.shortcuts import get_object_or_404
from django.views.generic import ListView

from gatheros_event.models import Event
from payment.models import Transaction


class EventPaymentView(ListView):

    template_name = 'payments/list.html'
    event = None

    def dispatch(self, request, *args, **kwargs):
        self.event = get_object_or_404(Event, pk=self.kwargs.get('pk'))
        response = super().dispatch(request, *args, **kwargs)
        return response

    def get_context_data(self, **kwargs):
        # noinspection PyUnresolvedReferences
        context = super(EventPaymentView, self).get_context_data(**kwargs)
        context['event'] = self.event

        return context

    def get_queryset(self):

        all_transactions = Transaction.objects.filter(subscription__event=self.event)

        return all_transactions
