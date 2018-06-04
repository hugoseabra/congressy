from django.contrib import admin

from .models import (
    OptionalServiceType,
    OptionalProductType,
    Product,
    Service,
    SubscriptionProduct,
    SubscriptionService,
    Theme,
)

admin.site.register(Theme)
admin.site.register(OptionalServiceType)
admin.site.register(OptionalProductType)


@admin.register(Service)
class OptionalServiceAdmin(admin.ModelAdmin):
    search_fields = (
        'lot_category__event__name',
        'lot_category__lots__name',
        'theme__name',
        'optional_type__name',
        'name',
    )
    list_filter = ('restrict_unique',)
    list_display = (
        'name',
        'theme',
        'lot_category',
        'quantity',
        'liquid_price',
    )
    fieldsets = (
        (None, {
            'fields': (
                'optional_type',
                'lot_category',
                'theme',
                'name',
                'schedule_start',
                'schedule_end',
                'date_end_sub',
                'created_by',
                'modified_by',
                'published',
                'description',
            ),
        }),
        ('Preços e Restrições', {
            'fields': (
                'liquid_price',
                'restrict_unique',
                'quantity',
                'release_days',
            ),
        }),
    )


@admin.register(Product)
class OptionalProductAdmin(admin.ModelAdmin):
    search_fields = (
        'lot_category__event__name',
        'lot_category__lots__name',
        'optional_type__name',
        'name',
    )
    list_display = (
        'name',
        'lot_category',
        'quantity',
        'liquid_price',
    )
    fieldsets = (
        (None, {
            'fields': (
                'optional_type',
                'lot_category',
                'name',
                'date_end_sub',
                'created_by',
                'modified_by',
                'published',
                'description',
            ),
        }),
        ('Preços e Restrições', {
            'fields': (
                'liquid_price',
                'quantity',
                'release_days',
            ),
        }),
    )


admin.site.register(SubscriptionProduct)
admin.site.register(SubscriptionService)
