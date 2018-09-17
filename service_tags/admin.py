from django.contrib import admin

from service_tags import forms


@admin.register(forms.CustomServiceTag)
class CertificateAdmin(admin.ModelAdmin):
    form = forms.CustomServiceTagForm
