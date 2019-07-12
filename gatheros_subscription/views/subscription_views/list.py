import locale
from collections import OrderedDict
from functools import cmp_to_key

from django.core.exceptions import ObjectDoesNotExist
from django.views import generic

from gatheros_event.helpers.event_business import is_paid_event
from gatheros_subscription.models import (
    Subscription, LotCategory, Lot)
from gatheros_subscription.views import SubscriptionViewMixin
from ticket.models import Ticket


class SubscriptionListView(SubscriptionViewMixin, generic.TemplateView):
    """ Lista de inscrições """

    model = Subscription
    template_name = 'subscription/list.html'
    has_filter = False

    def get_context_data(self, **kwargs):
        cxt = super().get_context_data(**kwargs)

        cxt.update({
            'has_subs': Subscription.objects.all_completed().filter(
                event_id=self.event.id,
            ).count() > 0,
            'group_tags': self.get_group_tags(),
            'tickets': self.get_tickets(),
            'has_filter': self.has_filter,
            'event_is_paid': is_paid_event(self.event),
            'has_inside_bar': True,
            'active': 'inscricoes',
            'accreditation_service': self.get_accreditation_service()
        })
        return cxt

    def can_access(self):
        return self.request.user.has_perm(
            'gatheros_event.can_manage_subscriptions',
            self.get_event()
        )

    def get_group_tags(self):

        group_tags = list()

        for sub in self.event.subscriptions.all():

            if sub.tag_group:

                tag_group = str.strip(sub.tag_group)
                if tag_group not in group_tags:
                    group_tags.append(tag_group)

        self.has_filter = len(group_tags) > 0

        return sorted(group_tags, key=cmp_to_key(locale.strcoll))

    def get_tickets(self):

        tickets = \
            Ticket.objects.filter(
                event_id=self.event.pk,
                num_subs__gt=0,
            ).order_by('name')

        if self.has_filter is False:
            self.has_filter = tickets.count() > 0

        return tickets

    def get_accreditation_service(self):
        try:
            return self.event.attendance_services.get(accreditation=True)

        except ObjectDoesNotExist:
            return None
