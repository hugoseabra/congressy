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
    inlines = [PartnerContractAdminInline]
    form = forms.PartnerContractForm
    ordering = ('person__name',)
    list_display = (
        'get_name',
        'get_email',
        'status',
        'get_num_contracts',
        'approved',
    )
    fields = (
        'person',
        'status',
        'approved',
    )
    readonly_fields = ('person',)

    def has_add_permission(self, request):
        return False

    def get_name(self, instance):
        return instance.person.name

    def get_email(self, instance):
        return instance.person.email

    def get_num_contracts(self, instance):
        return instance.contracts.count()

    get_name.__name__ = 'nome'
    get_email.__name__ = 'e-mail'
    get_num_contracts.__name__ = '# Contratos'


@admin.register(PartnerPlan)
class PartnerPlanAdmin(admin.ModelAdmin):
    form = forms.PartnerPlanForm
    list_display = ('name', 'percent')
