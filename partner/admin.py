"""
Django Admin for Partners
"""
from django.contrib import admin

from .models import Partner, PartnerPlan, PartnerContract
from .forms import PartnerContractForm

@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('person', 'status')


@admin.register(PartnerPlan)
class PartnerPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'percent')


@admin.register(PartnerContract)
class PartnerContractAdmin(admin.ModelAdmin):
    form = PartnerContractForm
    list_display = ('event', 'partner')

