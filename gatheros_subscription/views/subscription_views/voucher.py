from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse

from gatheros_event.views.mixins import AccountMixin
from gatheros_subscription.helpers.voucher import create_voucher, \
    get_voucher_file_name
from gatheros_subscription.models import (
    Subscription,
)


class VoucherSubscriptionPDFView(AccountMixin):

    def __init__(self, *args, **kwargs):
        self.subscription = None
        super().__init__(*args, **kwargs)

    def pre_dispatch(self, request):
        uuid = self.kwargs.get('pk')
        self.subscription = get_object_or_404(Subscription,
                                              uuid=uuid)

        return super().pre_dispatch(request)

    def get_permission_denied_url(self):
        return reverse(
            'subscription:subscription-view', kwargs={
                'event_pk': self.subscription.event_id,
                'pk': self.subscription.pk,
            }
        )

    def can_access(self):
        return self.subscription.confirmed is True

    def get(self, request, *args, **kwargs):
        pdf = create_voucher(subscription=self.subscription, save=True,
                             force=True)
        pdf_content = open(pdf, 'rb')

        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="{}"'.format(
            get_voucher_file_name(subscription=self.subscription)
        )

        return response
