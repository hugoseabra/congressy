from django.contrib import admin

from associate.models import Associate


@admin.register(Associate)
class NameActivePKAdmin(admin.ModelAdmin):
    """Base class para modelos que possuem campos 'active' e 'name'"""
    list_display = ('name', 'active', 'pk')
