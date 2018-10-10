from django.contrib import admin

from mix_boleto import models


@admin.register(models.SyncResource)
class SyncResourceAdmin(admin.ModelAdmin):
    search_fields = (
        'alias',
    )
    list_display = (
        'alias',
        'db_name',
        'pk'
    )
