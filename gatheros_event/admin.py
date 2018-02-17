# pylint: disable=W0222
"""
Django Admin para Gatheros Event
"""
from django.contrib import admin

from .models import Category, Event, Info, Invitation, Member, Occupation, \
    Organization, Person, Place, Segment, Subject


@admin.register(Segment)
@admin.register(Subject)
@admin.register(Occupation)
@admin.register(Category)
class NameActivePKAdmin(admin.ModelAdmin):
    """Base class para modelos que possuem campos 'active' e 'name'"""
    list_display = ('name', 'active', 'pk')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """
    Admin para Event
    """
    list_display = (
        'name',
        'organization',
        'subscription_type',
        'category',
        'date_start',
        'date_end',
        'get_percent_completed',
        'get_percent_attended',
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
                'image_main',
                'published',
                'slug',
            ),
        }),
        ('Inscrições', {
            'fields': ('subscription_type', 'subscription_offline'),
        }),
        ('Publicação', {
            'fields': (
                'image_main',
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

    def get_percent_completed(self, instance):
        if not instance.limit:
            return 'Livre'

        remaining = instance.limit - instance.subscriptions.count()
        percent = '{0:.2f}'.format(100 - instance.percent_completed)
        return '{} ({}%)'.format(remaining, percent)

    def get_percent_attended(self, instance):
        queryset = instance.subscriptions
        return '{}/{} ({}%)'.format(
            queryset.filter(attended=True).count(),
            queryset.count(),
            '{0:.2f}'.format(instance.percent_attended)
        )

    get_percent_completed.__name__ = 'Vagas restantes'
    get_percent_attended.__name__ = 'Credenciados'


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    """
    Admin para Person
    """
    search_fields = ('name', 'email',)
    list_display = ('name', 'gender', 'user', 'created')
    ordering = ('created', 'name')
    readonly_fields = [
        'synchronized',
        'term_version',
        'politics_version'
    ]

    fieldsets = (
        (None, {
            'fields': (
                'name',
                'gender',
                'pne',
                'birth_date',
                'cpf',
                'rg',
                'orgao_expedidor',
                'avatar',
                'user',
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
    """
    Admin para Organization
    """
    search_fields = ('name',)
    list_display = ('name', 'active', 'internal')
    fieldsets = (
        (None, {
            'fields': (
                'name',
                'slug',
                'description_html',
                'avatar',
                'active',
                'internal',
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
        ('Dados Bancários', {
            'fields': (
                'bank_code',
                'agency',
                'agencia_dv',
                'account',
                'conta_dv',
                'document_type',
                'cnpj_ou_cpf',
                'legal_name',
                'account_type',
                'bank_account_id',
                'active_recipient',
                'recipient_id',
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
    """
    Admin para Place
    """
    list_display = ('name', 'event', 'pk')
    fieldsets = (
        (None, {
            'fields': (
                'name',
                'event',
                'show_location',
                'lat',
                'long',
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
        # ('Google Maps (Street View)', {
        #     'fields': (
        #         'google_street_view_link',
        #     ),
        # }),
    )


@admin.register(Info)
class EventInfoAdmin(admin.ModelAdmin):
    """
    Admin para Event Info
    """
    list_display = ('event', 'config_type', 'pk')
    exclude = ('description',)


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    """
    Admin para Member
    """
    search_fields = ('persno__name', 'person__email', 'organization__name',)
    list_display = ('organization', 'person', 'group', 'pk')
    ordering = ('organization', 'person')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "person":
            query_set = Person.objects.order_by('name')
            kwargs["queryset"] = query_set

        return super(MemberAdmin, self).formfield_for_foreignkey(
            db_field,
            request,
            **kwargs
        )


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    """
    Admin para Invitation
    """
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
        """Valor para coluna 'Organização'"""
        return instance.author.organization

    def get_user(self, instance):
        """Valor para coluna 'Usuário'"""
        return '{} {} ({})'.format(
            instance.to.first_name,
            instance.to.last_name,
            instance.to.email
        )

    get_organization.__name__ = 'organização'
    get_user.__name__ = 'convidado'
