from django.contrib import admin

from associate.models import Associate


@admin.register(Associate)
class AssociateAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'organization', 'pk')
