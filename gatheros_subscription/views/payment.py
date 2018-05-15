from django.views import generic

from payment.models import Transaction
from .subscription import EventViewMixin


class SubscriptionPaymentsView(EventViewMixin, generic.TemplateView):
    template_name = 'subscription/subscription-payments-list.html'
    queryset = Transaction.objects.get_queryset()
    lots = {}

    def get_queryset(self):
        return self.queryset.filter(subscription__uuid=self.kwargs.get('pk'))

    def get_transaction_lots(self):
        if self.lots:
            return self.lots

        queryset = self.get_queryset()

        for transaction in queryset.order_by('subscription__lot__name'):
            lot = transaction.subscription.lot
            self.lots[lot.pk] = lot

        return self.lots

    def get_context_data(self, **kwargs):
        cxt = super().get_context_data(**kwargs)
        cxt['lots'] = self.get_transaction_lots()
        return cxt
