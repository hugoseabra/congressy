# pylint: disable=W0222
"""
Django Admin para Partners
"""
from django.contrib import admin

from .models import Partner, PartnerPlan, PartnerContract

admin.site.register(Partner)
admin.site.register(PartnerPlan)
admin.site.register(PartnerContract)

