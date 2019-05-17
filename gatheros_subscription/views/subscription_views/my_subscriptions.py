from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views import generic

from attendance.helpers.attendance import subscription_has_certificate
from gatheros_event.models import Person
from gatheros_event.views.mixins import AccountMixin
from gatheros_subscription.models import (
    Subscription,
)


class MySubscriptionsListView(AccountMixin, generic.ListView):
    """ Lista de inscrições """

    model = Subscription
    template_name = 'subscription/my_subscriptions.html'
    ordering = ('event__name', 'event__date_start', 'event__date_end',)
    has_filter = False
    permission_denied_url = reverse_lazy('front:start')

    def get_queryset(self):
        person = self.request.user.person
        query_set = super(MySubscriptionsListView, self).get_queryset()

        # notcheckedin = self.request.GET.get('notcheckedin')
        # if notcheckedin:
        #     query_set = query_set.filter(attended=False)
        #     self.has_filter = True
        #
        # pastevents = self.request.GET.get('pastevents')
        # now = datetime.now()
        # if pastevents:
        #     query_set = query_set.filter(event__date_end__lt=now)
        #     self.has_filter = True
        #
        # else:
        #     query_set = query_set.filter(event__date_start__gt=now)

        return query_set.filter(
            person=person,
            completed=True,
            test_subscription=False,
            event__published=True,
        )

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        if self.get_paginate_by(self.object_list) is not None and hasattr(
                self.object_list, 'exists'):
            is_empty = not self.object_list.exists()
        else:
            is_empty = len(self.object_list) == 0

        if is_empty:
            return redirect(reverse('event:event-list'))

        return response

    def get_context_data(self, **kwargs):
        cxt = super(MySubscriptionsListView, self).get_context_data(**kwargs)
        cxt['has_filter'] = self.has_filter
        cxt['filter_events'] = self.get_events()
        cxt['status_events'] = self.get_attendance_status_events()
        cxt['needs_boleto_link'] = self.check_if_needs_boleto_link()
        # cxt['filter_categories'] = self.get_categories()
        return cxt

    def get_categories(self):
        """ Resgata categorias das inscrições existentes. """
        queryset = self.get_queryset()
        return queryset.values(
            'event__category__name',
            'event__category__id'
        ).distinct().order_by('event__category__name')

    def get_events(self):
        """ Resgata eventos dos inscrições o usuário possui inscrições. """
        queryset = self.get_queryset()
        return queryset.values(
            'event__name',
            'event__id',
        ).distinct().order_by('event__name')

    def get_attendance_status_events(self):
        status_events = dict()
        subscription = self.get_queryset()
        for sub in subscription:
            status_events[sub.event_id] = subscription_has_certificate(sub.pk)

        return status_events

    def can_access(self):
        try:
            self.request.user.person
        except Person.DoesNotExist:
            return False
        else:
            return True

    def check_if_needs_boleto_link(self):
        for subscription in self.object_list:

            if subscription.status == subscription.AWAITING_STATUS:

                for transaction in subscription.transactions.all():
                    if transaction.status == transaction.WAITING_PAYMENT and \
                            transaction.type == 'boleto':
                        return True

        return False
