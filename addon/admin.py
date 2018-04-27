from django.contrib import admin

from .models import Service, Product, SubscriptionService, \
    SubscriptionProduct, Theme, OptionalType

admin.site.register(Service)
admin.site.register(Product)
admin.site.register(Theme)
admin.site.register(OptionalType)
admin.site.register(SubscriptionProduct)
admin.site.register(SubscriptionService)
