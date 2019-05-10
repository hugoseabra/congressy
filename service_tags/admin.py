from django.contrib import admin
from django_grappelli_custom_autocomplete.admin import CustomAutocompleteMixin

from service_tags import forms


@admin.register(forms.CustomServiceTag)
class CustomServiceTagAdmin(CustomAutocompleteMixin, admin.ModelAdmin):
    form = forms.CustomServiceTagForm
    list_display = ('event', 'has_tracking_script', 'has_conversion_script')
    ordering = ('event__name',)
    raw_id_fields = ['event']

    def has_tracking_script(self, instance):
        return instance.tracking_script is not None

    def has_conversion_script(self, instance):
        return instance.conversion_script is not None

    has_tracking_script.__name__ = 'Rastreador'
    has_tracking_script.boolean = True
    has_conversion_script.__name__ = 'Conversao'
    has_conversion_script.boolean = True
