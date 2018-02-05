# pylint: disable=W0222
"""
Django Admin para Payments
"""
from django.contrib import admin

from .models import Transaction, TransactionStatus

admin.site.register(Transaction)
admin.site.register(TransactionStatus)


