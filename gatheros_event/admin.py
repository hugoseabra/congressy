from django.contrib import admin
from .models import Segment, Subject, Occupation, Category, Person, Organization, Member, Place, Event, Info


class NamePKAdmin(admin.ModelAdmin):
    list_display = ('name', 'pk')


class NameActivePKAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'pk')


class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'subscription_type', 'category', 'place', 'pk')


class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'genre', 'record_type', 'user')
    readonly_fields = ['synchronized', 'term_version', 'politics_version']


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'internal')


class PlaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'pk')


class EventInfoAdmin(admin.ModelAdmin):
    list_display = ('event', 'pk')


class MemberAdmin(admin.ModelAdmin):
    list_display = ('person', 'organization', 'group', 'pk')


admin.site.register(Segment, NameActivePKAdmin)
admin.site.register(Subject, NameActivePKAdmin)
admin.site.register(Occupation, NameActivePKAdmin)
admin.site.register(Category, NameActivePKAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(Place, PlaceAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Info, EventInfoAdmin)
