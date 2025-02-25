# pylint: disable=C0103, E0401
"""
Gatheros Event Permission
"""
from django.core.exceptions import ImproperlyConfigured
from permission import add_permission_logic
from permission.compat import is_authenticated
from permission.logics.base import PermissionLogic
from permission.utils.field_lookup import field_lookup

from .models import Event, Invitation, Member, Organization, Person, Place


class MemberPermissionLogic(PermissionLogic):
    """
    Lógica de permissão baseada no relacionamento do usuário com organização.
    """
    def __init__(self, handler, permissions=None, field_organization=None):
        """
        Construtor

        handler : callable
            Irá lidar com usuário e organização devolvendo um boolean de acordo
            com sua lógica interna

        permissions : list
            Lista das permissões caso handler devolva True

        field_organization : string | None
            Qual campo de 'obj' em has_perm está a organização, se None o
            próprio 'obj' é uma organização
        """
        self.handler = handler
        self.permissions = permissions
        self.field_organization = field_organization

    def has_perm(self, user_obj, perm, obj=None):
        """
        Verifica se existe permissão do usuário de acordo com a permissão e
        handler de lógica de permissão.
        """
        if not is_authenticated(user_obj):
            return False

        if self.field_organization:
            obj = field_lookup(obj, self.field_organization)

        if obj and not isinstance(obj, Organization):
            raise ImproperlyConfigured(
                'Configuração errada, "obj" não é do tipo "Organization". '
                'Verfique o parametro "field_organization" em '
                'add_permission_logic. Lógica inserida: {handler_name},'
                ' permissões configuradas ({permissions}) e'
                ' permissão solicitada: {required_permission}'.format(
                    handler_name=self.handler.__name__,
                    permissions=', '.join(self.permissions),
                    required_permission=perm
                )
            )

        has_perm = perm.split('.')[1] in self.permissions
        perm_granted = self.handler(user_obj=user_obj, organization=obj)

        return has_perm and perm_granted


# Handlers
def member_is_admin(user_obj, organization=None):
    """
    Usuário é membro ativo de organização e administrador.

    :param user_obj: Instância de usuário
    :param organization: Instância de organização
    :return: bool
    """
    person = Person.objects.get(user=user_obj)
    is_auth = user_obj.is_authenticated()
    is_admin = organization and organization.is_admin(person)
    is_member_active = organization and organization.is_member_active(person)

    return is_auth and is_admin and is_member_active


def member_is_admin_not_internal(user_obj, organization=None):
    """
    Usuário é membro ativo de organização não interna e administrador.

    :param user_obj: Instância de usuário
    :param organization: Instância de organização
    :return: bool
    """
    if not organization or organization.internal:
        return False

    person = Person.objects.get(user=user_obj)
    is_auth = user_obj.is_authenticated()
    is_admin = organization and organization.is_admin(person)
    is_member_active = organization and organization.is_member_active(person)

    return is_auth and is_admin and is_member_active


def member_is_admin_and_internal(user_obj, organization=None):
    """
    Usuário é membro ativo de organização  interna e administrador.

    :param user_obj: Instância de usuário
    :param organization: Instância de organização
    :return: bool
    """
    if not organization or not organization.internal:
        return False

    person = Person.objects.get(user=user_obj)
    is_auth = user_obj.is_authenticated()
    is_admin = organization and organization.is_admin(person)
    is_member_active = organization and organization.is_member_active(person)

    return is_auth and is_admin and is_member_active


def member_is_member(user_obj, organization):
    """
    Usuário é membro ativo da organização.

    :param user_obj: Instância de usuário
    :param organization: Instância de organização
    :return: bool
    """

    person = Person.objects.get(user=user_obj)
    is_auth = user_obj.is_authenticated()
    is_member = organization and organization.is_member(person)
    is_member_active = organization and organization.is_member_active(person)

    return is_auth and is_member and is_member_active


# Lógicas de permissões
# Organização -> Admin
logic = MemberPermissionLogic(
    member_is_admin,
    ['can_add_event'],
)
add_permission_logic(Organization, logic)

# Organização -> Admin -> Não Interno
logic = MemberPermissionLogic(
    member_is_admin_not_internal,
    [
        'can_view',
        'can_invite',
        'change_organization',
        'delete_organization',
        'can_manage_members',
    ],
)
add_permission_logic(Organization, logic)

# Organização -> Admin -> Interno
logic = MemberPermissionLogic(
    member_is_admin_and_internal,
    [
        'can_invite',
        'change_organization',
        'can_manage_members',
    ],
)
add_permission_logic(Organization, logic)

# Organização -> Membro
logic = MemberPermissionLogic(
    member_is_member,
    [
        'can_view',
        'can_view_members',
        'can_manage_places',
        'can_manage_fields',
    ],
)
add_permission_logic(Organization, logic)

# Organização -> Admin -> membros
logic = MemberPermissionLogic(
    member_is_admin_not_internal,
    [
        'change_member',
        'delete_member',
    ],
    'organization',
)
add_permission_logic(Member, logic)

# Organização -> Admin -> Event
logic = MemberPermissionLogic(
    member_is_admin,
    ['change_event', 'delete_event'],
    'organization',
)
add_permission_logic(Event, logic)

logic = MemberPermissionLogic(
    member_is_member,
    ['view_lots', 'view_form', 'can_add_lot', 'can_manage_subscriptions'],
    'organization',
)
add_permission_logic(Event, logic)


# Organização -> Admin -> Locais de evento
logic = MemberPermissionLogic(
    member_is_admin,
    ['delete_place'],
    'organization',
)
add_permission_logic(Place, logic)

# Organização -> Admin -> Invitation
logic = MemberPermissionLogic(
    member_is_admin_not_internal,
    ['delete_invitation'],
    'author__organization',
)
add_permission_logic(Invitation, logic)
