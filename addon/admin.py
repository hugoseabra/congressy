from django.contrib import admin
from django_grappelli_custom_autocomplete.admin import CustomAutocompleteMixin

from .models import (
    OptionalServiceType,
    OptionalProductType,
    Product,
    Service,
    SubscriptionProduct,
    SubscriptionService,
    Theme,
)

admin.site.register(OptionalServiceType)
admin.site.register(OptionalProductType)


@admin.register(Theme)
class ThemeAdmin(CustomAutocompleteMixin, admin.ModelAdmin):
    raw_id_fields = ['event']


@admin.register(Service)
class OptionalServiceAdmin(CustomAutocompleteMixin, admin.ModelAdmin):
    search_fields = (
        'ticket__event__name',
        'ticket__name',
        'theme__name',
        'optional_type__name',
        'name',
    )
    list_filter = ('restrict_unique',)
    list_display = (
        'name',
        'theme',
        'ticket',
        'quantity',
        'liquid_price',
    )
    raw_id_fields = ['theme', 'optional_type', 'ticket']
    fieldsets = (
        (None, {
            'fields': (
                'optional_type',
                'ticket',
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
class OptionalProductAdmin(CustomAutocompleteMixin, admin.ModelAdmin):
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
    raw_id_fields = ['optional_type', 'lot_category']
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
class OptionalSubscriptionServiceAdmin(CustomAutocompleteMixin,
                                       admin.ModelAdmin):
    fields = (
        'optional',
        'subscription',
    )

    raw_id_fields = ['optional', 'subscription']

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
        event_id = subscription_service.optional.lot_category.event_id

        context['adminform'].form.fields['optional'].queryset = \
            Service.objects.filter(
                published=True,
                lot_category__event_id=event_id,
            )

        response = super(OptionalSubscriptionServiceAdmin, self) \
            .render_change_form(request, context, *args, **kwargs)

        return response


@admin.register(SubscriptionProduct)
class OptionalSubscriptionProductAdmin(CustomAutocompleteMixin,
                                       admin.ModelAdmin):
    fields = (
        'optional',
        'subscription',
    )
    raw_id_fields = ['optional', 'subscription']

    search_fields = (
        'subscription__person__name',
        'subscription__person__email',
        'subscription__code',
    )

    list_display = (
        'get_person_name',
        'get_optional_name',
    )

    def render_change_form(self, request, context, *args, **kwargs):
        subscription_product = kwargs.get('obj')
        event_id = subscription_product.optional.lot_category.event_id

        context['adminform'].form.fields['optional'].queryset = \
            Product.objects.filter(
                published=True,
                lot_category__event_id=event_id,
            )

        response = super(OptionalSubscriptionProductAdmin, self) \
            .render_change_form(request, context, *args, **kwargs)

        return response
