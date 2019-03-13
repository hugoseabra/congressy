from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from gatheros_event.views.mixins import AccountMixin
from gatheros_subscription.helpers.voucher import create_voucher, get_voucher_file_name
from gatheros_subscription.models import (
    Subscription,
)


class VoucherSubscriptionPDFView(AccountMixin):

    def pre_dispatch(self, request):
        uuid = self.kwargs.get('pk')
        self.subscription = get_object_or_404(Subscription,
                                              uuid=uuid)

        return super().pre_dispatch(request)

    def get(self, request, *args, **kwargs):
        pdf = create_voucher(subscription=self.subscription)
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="{}"'.format(
            get_voucher_file_name(subscription=self.subscription)
        )

        return response