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


@admin.register(SubscriptionService)
class OptionalSubscriptionServiceAdmin(admin.ModelAdmin):
    fields = (
        'optional',
    )

    search_fields = (
        'subscription__person__name',
        'subscription__person__email',
        'subscription__code',
    )

    list_display = (
        'get_person_name',
        'get_optional_name',
        'get_theme',
    )

    def render_change_form(self, request, context, *args, **kwargs):
        subscription_service = kwargs.get('obj')
        lot_category_id = subscription_service.optional.lot_category_id

        context['adminform'].form.fields['optional'].queryset = \
            Service.objects.filter(
                published=True,
                lot_category_id=lot_category_id,
            )

        response = super(OptionalSubscriptionServiceAdmin, self) \
            .render_change_form(request, context, *args, **kwargs)

        return response


@admin.register(SubscriptionProduct)
class OptionalSubscriptionProductAdmin(admin.ModelAdmin):
    fields = (
        'optional',
    )

    search_fields = (
        'subscription__person__name',
        'subscription__person__email',
        'subscription__code',
    )

    list_display = (
        'get_person_name',
        'get_optional_name',
        'get_theme',
    )

    def render_change_form(self, request, context, *args, **kwargs):
        subscription_product = kwargs.get('obj')
        lot_category_id = subscription_product.optional.lot_category_id

        context['adminform'].form.fields['optional'].queryset = \
            Product.objects.filter(
                published=True,
                lot_category_id=lot_category_id,
            )

        response = super(OptionalSubscriptionProductAdmin, self) \
            .render_change_form(request, context, *args, **kwargs)

        return response
