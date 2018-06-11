# pylint: disable=W0222
"""
Django Admin para Payments
"""
from django.contrib import admin

from .models import BankAccount, Transaction, TransactionStatus


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    search_fields = (
        'uuid',
        'subscription__uuid',
        'subscription__person__uuid',
        'subscription__person__name',
        'subscription__event__name',
    )
    list_display = (
        'subscription',
        'status',
        'type',
        'date_created',
        'liquid_amount',
        'amount',
    )


@admin.register(TransactionStatus)
class TransactionStatusAdmin(admin.ModelAdmin):
    search_fields = (
        'transaction__subscription__person__name',
        'transaction__subscription__event__name',
    )
    list_display = ('transaction', 'date_created', 'status')


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ('document_number', 'date_created', 'ativo', 'recipient_id')
