import locale
from django.views import generic
from functools import cmp_to_key

from gatheros_event.helpers.event_business import is_paid_event
from gatheros_subscription.models import (
    Subscription)
from gatheros_subscription.views import SubscriptionViewMixin


class SubscriptionListView(SubscriptionViewMixin, generic.TemplateView):
    """ Lista de inscrições """

    model = Subscription
    template_name = 'subscription/list.html'

    def get_context_data(self, **kwargs):
        cxt = super().get_context_data(**kwargs)

        cxt.update({
            'has_subs': Subscription.objects.filter(
                event_id=self.event.id,
                completed=True,
                test_subscription=False,
            ).count() > 0,
            'institutions': self.get_institutions(),
            'group_tags': self.get_group_tags(),
            'lots': self.get_lots(),
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

    def get_institutions(self):
        institutions = list()

        for sub in self.event.subscriptions.all():

            if sub.person.institution:

                institution = str.strip(sub.person.institution)
                if institution not in institutions:
                    institutions.append(institution)

        return sorted(institutions, key=cmp_to_key(locale.strcoll))

    def get_group_tags(self):

        group_tags = list()

        for sub in self.event.subscriptions.all():

            if sub.tag_group:

                tag_group = str.strip(sub.tag_group)
                if tag_group not in group_tags:
                    group_tags.append(tag_group)

        return sorted(group_tags, key=cmp_to_key(locale.strcoll))

    #
    # def get_categories(self):
    #
    #     categories = dict()
    #
    #     for cat in LotCategory.objects.filter(event=self.event):
    #         if cat.pk not in categories.values():
    #             categories[cat.name] = cat.pk
    #
    #     sorted_categories = OrderedDict()
    #
    #     for name in sorted(categories.keys(), key=cmp_to_key(locale.strcoll)):
    #         for _name, pk in categories.items():
    #             if name == _name:
    #                 sorted_categories[name] = pk
    #
    #     return sorted_categories
    #
    # def get_lots(self):
    #
    #     lots = dict()
    #
    #     for lot in Lot.objects.filter(event=self.event, internal=False):
    #
    #         if lot.pk not in lots.values():
    #             lots[lot.name] = lot.pk
    #
    #     sorted_lots = OrderedDict()
    #
    #     for name in sorted(lots.keys(), key=cmp_to_key(locale.strcoll)):
    #         for _name, pk in lots.items():
    #             if name == _name:
    #                 sorted_lots[name] = pk
    #
    #     return sorted_lots
