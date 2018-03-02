"""
Django Admin for Partners
"""
from datetime import datetime

from django.contrib import admin

from gatheros_event.models import Event
from . import forms
from .models import Partner, PartnerPlan, PartnerContract


class PartnerContractAdminInline(admin.StackedInline):
    model = PartnerContract
    form = forms.PartnerContractForm
    extra = 0

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "event":
            kwargs["queryset"] = Event.objects \
                .filter(date_start__gte=datetime.now()) \
                .order_by('name')

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    search_fields = (
        'person__name',
        'bank_account__legal_name',
        'contracts__event__name',
        'contracts__partner_plan__name',
    )

    inlines = [PartnerContractAdminInline]
    form = forms.PartnerForm
    ordering = ('person__name', 'bank_account__legal_name',)
    list_display = (
        'get_name',
        'get_email',
        'status',
        'get_num_contracts',
        'get_legal_name',
        'has_account',
        'approved',
    )
    fields = (
        'person',
        'status',
        'approved',
        'bank_account',
    )
    readonly_fields = ('person', 'bank_account',)

    def has_add_permission(self, request):
        return False

    def get_name(self, instance):
        return instance.person.name

    def get_email(self, instance):
        return instance.person.email

    def get_num_contracts(self, instance):
        return instance.contracts.count()

    def has_account(self, instance):
        try:
            instance.bank_account.recipient_id
        except AttributeError:
            return False

        return True

    def get_legal_name(self, instance):
        try:
            return instance.bank_account.legal_name
        except AttributeError:
            return '-'

    get_name.__name__ = 'nome'
    get_legal_name.__name__ = 'titular'
    get_email.__name__ = 'e-mail'
    get_num_contracts.__name__ = '# Contratos'
    has_account.__name__ = 'Conta'
    has_account.boolean = True


@admin.register(PartnerPlan)
class PartnerPlanAdmin(admin.ModelAdmin):
    form = forms.PartnerPlanForm
    list_display = ('name', 'percent')
