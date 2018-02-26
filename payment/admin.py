# pylint: disable=W0222
"""
Django Admin para Payments
"""
from django.contrib import admin

from .models import Transaction, TransactionStatus

admin.site.register(TransactionStatus)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    search_fields = (
        'subscription__person__name',
        'subscription__event__name',
    )


