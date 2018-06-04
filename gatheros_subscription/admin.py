from django.contrib import admin

from .models import (
    EventSurvey,
    LotCategory,
    Lot,
    Subscription,
)


@admin.register(LotCategory)
class LotCategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Lot)
class LotAdmin(admin.ModelAdmin):
    search_fields = (
        'event__name',
        'name',
    )
    list_display = (
        'name',
        'category',
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
                'category',
                'name',
                'event',
                'date_start',
                'date_end',
                'limit',
                'private',
                'internal',
                'event_survey',
            ),
        }),
        ('Preços e Formas de recebimento', {
            'fields': (
                'exhibition_code',
                'promo_code',
                'price',
                'tax',
                'discount',
                'discount_type',
                'transfer_tax',
            ),
        }),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        path = request.META['PATH_INFO']
        if db_field.name == "event_survey" and 'change' in path:
            lot_id = request.META['PATH_INFO'].split('/')[-3]
            lot = Lot.objects.get(pk=int(lot_id))
            kwargs["queryset"] = EventSurvey.objects.filter(event=lot.event)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_percent_completed(self, instance):
        if not instance.limit:
            return 'Livre'

        remaining = instance.limit - instance.subscriptions.exclude(
            status=Subscription.CANCELED_STATUS,
            completed=False,
        ).count()
        percent = '{0:.2f}'.format(100 - instance.percent_completed)
        return '{} ({}%)'.format(remaining, percent)

    def get_percent_attended(self, instance):
        queryset = instance.subscriptions.exclude(
            status=Subscription.CANCELED_STATUS,
            completed=False,
        )
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
    list_filter = ('completed',)
    readonly_fields = [
        'event',
        'code',
        'count',
        'attended',
        'attended_on',
        'completed',
        'synchronized',
        'congressy_percent',
    ]
    ordering = ('lot', 'count', 'person',)
