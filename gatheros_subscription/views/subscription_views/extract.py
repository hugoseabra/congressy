from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse

from gatheros_event.views.mixins import AccountMixin
from gatheros_subscription.helpers.extract import (
    create_extract,
    get_extract_file_name,
)
from gatheros_subscription.models import Subscription


class ExtractSubscriptionPDFView(AccountMixin):
    subscription = None

    def pre_dispatch(self, request):
        uuid = self.kwargs.get('pk')
        self.subscription = get_object_or_404(Subscription,
                                              uuid=uuid)

        return super().pre_dispatch(request)

    def get_permission_denied_url(self):
        """ Resgata url quando permissão negada. """
        return reverse('subscription:subscription-view', kwargs={
            'event_pk': self.kwargs.get('event_pk'),
            'pk': self.kwargs.get('pk'),
        })

    def get(self, request, *args, **kwargs):
        pdf = create_extract(subscription=self.subscription,
                             user=self.request.user)
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="{}"'.format(
            get_extract_file_name(subscription=self.subscription)
        )

        return response

    def can_access(self):
        return self.subscription.lot.price > 0
