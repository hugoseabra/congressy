from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import generic

from gatheros_subscription.helpers import report_payment
from payment.models import Transaction
from .subscription import EventViewMixin, PermissionDenied


class PaymentDeleteView(EventViewMixin, generic.View):
    http_method_names = ['post']
    queryset = Transaction.objects.get_queryset()
    object = None
    subscription = None

    def get_object(self):
        if self.object:
            return self.object

        self.object = get_object_or_404(
            Transaction, pk=self.request.POST.get('transaction_id')
        )
        self.subscription = self.object.subscription
        return self.object

    def pre_dispatch(self, request):
        self.event = self.get_event()

        if self.event.allow_internal_subscription is False:
            self.permission_denied_url = reverse(
                'subscription:subscription-list', kwargs={
                    'event_pk': self.event.pk,
                }
            )
            raise PermissionDenied('Você não pode realizar esta ação.')

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        url = reverse('subscription:subscription-payments', kwargs={
            'event_pk': self.event.pk,
            'pk': self.subscription.pk,
        })
        return url + '?details=1'

    def post(self, request, *args, **kwargs):
        url = self.get_success_url()

        self.object.delete()
        messages.success(request, 'Pagamento excluído com sucesso!')

        calculator = report_payment.PaymentReportCalculator(
            subscription=self.subscription
        )

        if not calculator.is_subscription_confirmed:
            self.subscription.status = self.subscription.AWAITING_STATUS
            self.subscription.save()

        return redirect(url)
