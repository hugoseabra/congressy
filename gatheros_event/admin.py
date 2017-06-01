from django.contrib import admin

from .models import Category, Event, Info, Invitation, Member, Occupation, \
    Organization, Person, Place, Segment, Subject


@admin.register(Segment)
@admin.register(Subject)
@admin.register(Occupation)
@admin.register(Category)
class NameActivePKAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'pk')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'organization',
        'subscription_type',
        'category',
        'date_start',
        'date_end',
        'published',
        'pk'
    )
    ordering = ['pk', 'name']
    readonly_fields = ['slug']

    fieldsets = (
        (None, {
            'fields': (
                'name',
                'organization',
                'category',
                'date_start',
                'date_end',
                'description',
                'published',
                'slug',
            ),
        }),
        ('Inscrições', {
            'fields': ('subscription_type', 'subscription_offline'),
        }),
        ('Publicação', {
            'fields': (
                'banner_top',
                'banner_small',
                'banner_slide',
                'website',
                'facebook',
                'twitter',
                'linkedin',
                'skype',
            ),
        }),
    )


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'gender', 'user', 'created')
    ordering = ('created', 'name')
    readonly_fields = [
        'user',
        'synchronized',
        'term_version',
        'politics_version'
    ]

    fieldsets = (
        (None, {
            'fields': (
                'name',
                'gender',
                'birth_date',
                'cpf',
                'rg',
                'orgao_expedidor',
                'avatar',
                'has_user',
            ),
        }),
        ('Contato', {
            'fields': (
                'email',
                'phone',
            ),
        }),
        ('Endereço', {
            'fields': (
                'zip_code',
                'street',
                'number',
                'complement',
                'village',
                'city',
            ),
        }),
        ('Site pessoal e Redes Sociais', {
            'fields': (
                'website',
                'facebook',
                'twitter',
                'linkedin',
                'skype',
            ),
        }),
        ('Termo de privacidade e política de uso', {
            'fields': (
                'term_version',
                'politics_version',
            ),
        }),
    )


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'internal')
    fieldsets = (
        (None, {
            'fields': (
                'name',
                'slug',
                'description',
                'active',
            ),
        }),
        ('Site e Redes Sociais', {
            'fields': (
                'website',
                'facebook',
                'twitter',
                'linkedin',
                'skype',
            ),
        }),
        ('Provedor de recebimento', {
            'fields': (
                'cash_provider',
                'cash_data',
            ),
        }),
    )


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'pk')
    fieldsets = (
        (None, {
            'fields': (
                'name',
                'organization',
            ),
        }),
        ('Endereço', {
            'fields': (
                'zip_code',
                'street',
                'number',
                'complement',
                'village',
                'city',
            ),
        }),
        ('Google Maps (Street View)', {
            'fields': (
                'google_street_view_link',
            ),
        }),
    )


@admin.register(Info)
class EventInfoAdmin(admin.ModelAdmin):
    list_display = ('event', 'pk')


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('organization', 'person', 'group', 'pk')
    ordering = ('organization', 'person')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "person":
            query_set = Person.objects.filter(has_user=True).order_by('name')
            kwargs["queryset"] = query_set

        return super(MemberAdmin, self).formfield_for_foreignkey(
            db_field,
            request,
            **kwargs
        )


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = (
        'author', 'get_user', 'get_organization', 'created', 'expired')
    readonly_fields = ['created', 'expired']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "author":
            kwargs["queryset"] = Member.objects.filter(
                group=Member.ADMIN,
                organization__internal=False
            )

        return super(InvitationAdmin, self).formfield_for_foreignkey(
            db_field,
            request,
            **kwargs
        )

    def get_organization(self, instance):
        return instance.author.organization

    def get_user(self, instance):
        return '{} {} ({})'.format(
            instance.to.first_name,
            instance.to.last_name,
            instance.to.email
        )

    get_organization.__name__ = 'organização'
    get_user.__name__ = 'convidado'
