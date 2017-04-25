from django.contrib import admin

from .models import Category, Event, Info, Invitation, Member, Occupation, Organization, Person, Place, Segment, Subject


@admin.register(Segment)
@admin.register(Subject)
@admin.register(Occupation)
@admin.register(Category)
class NameActivePKAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'pk')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'subscription_type', 'category', 'place', 'date_start', 'date_end', 'pk')
    ordering = ['pk', 'name']


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'genre', 'user', 'created')
    ordering = ('created', 'name')
    readonly_fields = ['user', 'synchronized', 'term_version', 'politics_version']


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'internal')


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'pk')


@admin.register(Info)
class EventInfoAdmin(admin.ModelAdmin):
    list_display = ('event', 'pk')


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('organization', 'person', 'group', 'pk')
    ordering = ('organization', 'person')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "person":
            kwargs["queryset"] = Person.objects.filter(has_user=True).order_by('name')

        return super(MemberAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ('author', 'get_user', 'get_organization', 'created', 'expired')
    readonly_fields = ['created', 'expired']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "author":
            kwargs["queryset"] = Member.objects.filter(group=Member.ADMIN, organization__internal=False)

        return super(InvitationAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_organization(self, instance):
        return instance.author.organization

    def get_user(self, instance):
        return '{} {} ({})'.format(instance.to.first_name, instance.to.last_name, instance.to.email)

    get_organization.__name__ = 'organização'
    get_user.__name__ = 'convidado'
