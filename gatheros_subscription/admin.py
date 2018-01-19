from django.contrib import admin
from django.db.models import Count, Q

from gatheros_event.models import Event
from .models import (
    Lot,
    Subscription,
)


@admin.register(Lot)
class LotAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'event',
        'price',
        'date_start',
        'date_end',
        'get_percent_completed',
        'get_percent_attended',
        'private',
        'internal',
        'pk'
    )
    fieldsets = (
        (None, {
            'fields': (
                'name',
                'event',
                'date_start',
                'date_end',
                'limit',
                'private',
                'internal',
            ),
        }),
        ('Preços e Formas de recebimento', {
            'fields': (
                'promo_code',
                'price',
                'tax',
                'discount',
                'discount_type',
                'transfer_tax',
            ),
        }),
    )

    def get_percent_completed(self, instance):
        if not instance.limit:
            return 'Livre'

        remaining = instance.limit - instance.subscriptions.count()
        percent = '{0:.2f}'.format(100 - instance.percent_completed)
        return '{} ({}%)'.format(remaining, percent)

    def get_percent_attended(self, instance):
        queryset = instance.subscriptions
        return '{}/{} ({}%)'.format(
            queryset.filter(attended=True).count(),
            queryset.count(),
            '{0:.2f}'.format(instance.percent_attended)
        )

    get_percent_completed.__name__ = 'Vagas restantes'
    get_percent_attended.__name__ = 'Credenciados'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "event":
            events = Event.objects.annotate(num_lots=Count('lots')).filter(
                Q(
                    subscription_type=Event.SUBSCRIPTION_SIMPLE,
                    num_lots__exact=0
                ) | Q(
                    subscription_type=Event.SUBSCRIPTION_BY_LOTS
                )
            )

            for event in events:
                is_simple = \
                    event.subscription_type == Event.SUBSCRIPTION_SIMPLE
                has_lots = event.lots.count() > 0
                if is_simple and has_lots:
                    continue

            kwargs["queryset"] = events

        return super(LotAdmin, self).formfield_for_foreignkey(
            db_field,
            request,
            **kwargs
        )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('person', 'count', 'lot', 'code', 'attended',)
    readonly_fields = [
        'event',
        'code',
        'count',
        'attended',
        'attended_on',
        'synchronized'
    ]
    ordering = ('lot', 'count', 'person',)
