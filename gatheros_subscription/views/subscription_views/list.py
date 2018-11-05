from django.views import generic

from gatheros_event.helpers.event_business import is_paid_event
from gatheros_subscription.models import (
    Subscription,
)
from gatheros_subscription.views import SubscriptionViewMixin


class SubscriptionListView(SubscriptionViewMixin, generic.ListView):
    """ Lista de inscrições """

    model = Subscription
    template_name = 'subscription/list.html'
    has_filter = False

    def get_queryset(self):
        query_set = super(SubscriptionListView, self).get_queryset()

        lots = self.request.GET.getlist('lots', [])
        if lots:
            query_set = query_set.filter(lot_id__in=lots)
            self.has_filter = True

        has_profile = self.request.GET.get('has_profile')
        if has_profile:
            query_set = query_set.filter(person__user__isnull=False)
            self.has_filter = True

        event = self.get_event()

        return query_set.filter(event=event, completed=True)

    def get_context_data(self, **kwargs):
        cxt = super().get_context_data(**kwargs)

        cxt.update({
            'can_add_subscription': self.can_add_subscription(),
            'lots': self.get_lots(),
            'has_filter': self.has_filter,
            'event_is_paid': is_paid_event(self.event),
            'has_inside_bar': True,
            'active': 'inscricoes',
        })
        return cxt

    def can_access(self):
        return self.request.user.has_perm(
            'gatheros_event.can_manage_subscriptions',
            self.get_event()
        )

    def can_add_subscription(self):
        event = self.get_event()
        if event.subscription_type == event.SUBSCRIPTION_SIMPLE:
            return True

        num_lots = self.get_num_lots()
        return num_lots > 0
