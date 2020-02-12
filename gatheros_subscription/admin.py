from django.contrib import admin

from .models import (
    EventSurvey,
    LotCategory,
    Lot,
    Subscription,
    FormConfig,
)


@admin.register(FormConfig)
class FormConfigAdmin(admin.ModelAdmin):
    search_fields = (
        'event__name',      
    )
    raw_id_fields = ['event']


@admin.register(LotCategory)
class LotCategoryAdmin(admin.ModelAdmin):
    search_fields = (
        'event__name',
    )
    raw_id_fields = ['event']


@admin.register(Lot)
class LotAdmin(admin.ModelAdmin):
    search_fields = (
        'pk',
        'event__name',
        'event__slug',
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
        'private',
        'internal',
        'pk'
    )
    raw_id_fields = ['category']
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

        remaining = instance.limit - instance.subscriptions.filter(
            completed=True, test_subscription=False
        ).exclude(
            status=Subscription.CANCELED_STATUS,
        ).count()
        percent = '{0:.2f}'.format(100 - instance.percent_completed)
        return '{} ({}%)'.format(remaining, percent)

    get_percent_completed.__name__ = 'Vagas restantes'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    search_fields = (
        'uuid',
        'code',
        'person__uuid',
        'person__name',
        'person__email',
        'person__cpf',
        'event__name',
        'event__slug',
    )
    list_display = ('person', 'event_count', 'lot', 'code', 'completed',)
    list_filter = ('completed',)
    readonly_fields = [
        'event',
        'code',
        'count',
        'event_count',
        'synchronized',
        'attended',
        'created_by',
        'congressy_percent',
    ]
    ordering = ('lot', 'event_count', 'person',)
    raw_id_fields = ['lot', 'person', 'author']

    def has_add_permission(self, request):
        return False
