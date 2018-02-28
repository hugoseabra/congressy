# pylint: disable=W0222
"""
Django Admin para Payments
"""
from django.contrib import admin

from .models import Transaction, TransactionStatus


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    search_fields = (
        'subscription__person__name',
        'subscription__event__name',
    )
    list_display = ('subscription', 'status', 'type', 'date_created', 'amount')


@admin.register(TransactionStatus)
class TransactionStatusAdmin(admin.ModelAdmin):
    search_fields = (
        'transaction__subscription__person__name',
        'transaction__subscription__event__name',
    )
    list_display = ('transaction', 'date_created', 'status')
