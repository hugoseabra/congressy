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
        'price',
    )
    fieldsets = (
        (None, {
            'fields': (
                'optional_type',
                'lot_category',
                'theme',
                'name',
                'date_start',
                'date_end',
                'description',
                'created_by',
                'modified_by',
                'published',
            ),
        }),
        ('Preços e Restrições', {
            'fields': (
                'price',
                'restrict_unique',
                'quantity',
                'release_days',
            ),
        }),
    )


admin.site.register(Product)
admin.site.register(SubscriptionProduct)
admin.site.register(SubscriptionService)
