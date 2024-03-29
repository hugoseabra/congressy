import locale
from collections import OrderedDict
from functools import cmp_to_key

from django.core.exceptions import ObjectDoesNotExist
from django.views import generic

from gatheros_event.helpers.event_business import is_paid_event
from gatheros_subscription.models import (
    Subscription, LotCategory, Lot)
from gatheros_subscription.views import SubscriptionViewMixin


class SubscriptionListView(SubscriptionViewMixin, generic.TemplateView):
    """ Lista de inscrições """

    model = Subscription
    template_name = 'subscription/list.html'
    has_filter = False

    def get_context_data(self, **kwargs):
        cxt = super().get_context_data(**kwargs)

        cxt.update({
            'has_subs': Subscription.objects.filter(
                event_id=self.event.id,
                completed=True,
                test_subscription=False,
            ).count() > 0,
            'group_tags': self.get_group_tags(),
            'categories': self.get_categories(),
            'lots': self.get_lots(),
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

    def get_categories(self):

        categories = dict()

        for cat in LotCategory.objects.filter(event=self.event):
            if cat.pk not in categories.values():
                categories[cat.name] = cat.pk

        sorted_categories = OrderedDict()

        for name in sorted(categories.keys(), key=cmp_to_key(locale.strcoll)):
            for _name, pk in categories.items():
                if name == _name:
                    sorted_categories[name] = pk

        self.has_filter = len(sorted_categories) > 0

        return sorted_categories

    def get_lots(self):

        categories = dict()

        for cat in LotCategory.objects.filter(event=self.event):
            if cat.pk not in categories.keys():
                categories[cat.pk] = dict()

        for lot in Lot.objects.filter(event=self.event, internal=False):

            if lot.category.pk not in categories.keys():
                categories[lot.category.pk] = dict()

            if lot.pk not in categories[lot.category.pk].keys():
                categories[lot.category.pk][lot.pk] = lot.name

        return categories

    def get_accreditation_service(self):
        try:
            return self.event.attendance_services.get(accreditation=True)

        except ObjectDoesNotExist:
            return None
