from django.contrib import admin

from .models import (
    Lot,
    Subscription,
)


@admin.register(Lot)
class LotAdmin(admin.ModelAdmin):
    search_fields = (
        'event__name',
        'name',
    )
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


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    search_fields = (
        'uuid',
        'person__uuid',
        'person__name',
        'person__email',
        'created',
        'event__name',
    )
    list_display = ('person', 'count', 'lot', 'code', 'attended',)
    readonly_fields = [
        'event',
        'code',
        'count',
        'attended',
        'attended_on',
        'synchronized',
        'congressy_percent',
    ]
    ordering = ('lot', 'count', 'person',)
