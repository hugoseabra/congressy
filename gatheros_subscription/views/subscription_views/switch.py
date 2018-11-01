from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views import generic

from gatheros_subscription.models import (
    Subscription,
)
from gatheros_subscription.views import SubscriptionViewMixin


class SwitchSubscriptionTestView(SubscriptionViewMixin, generic.View):
    """
    Gerenciamento de inscrições que podem ou não serem setados como Teste.
    """
    success_message = ""

    def get_object(self):
        return get_object_or_404(Subscription, pk=self.kwargs.get('pk'))

    def post(self, request, *args, **kwargs):
        state = request.POST.get('state')

        subscription = self.get_object()
        subscription.test_subscription = state == "True"
        subscription.save()
        return HttpResponse(status=200)
