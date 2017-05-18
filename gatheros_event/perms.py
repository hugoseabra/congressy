from django.core.exceptions import ImproperlyConfigured
from permission import add_permission_logic
from permission.compat import is_authenticated
from permission.logics.base import PermissionLogic
from permission.utils.field_lookup import field_lookup

from .models import Event, Member, Organization, Person


class MemberPermissionLogic(PermissionLogic):
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
        if not is_authenticated(user_obj):
            return False

        if self.field_organization:
            obj = field_lookup(obj, self.field_organization)

        if obj and not isinstance(obj, Organization):
            raise ImproperlyConfigured(
                'Configuração errada, "obj" não é do tipo "Organization". '
                'Verfique o parametro "field_organization" em '
                'add_permission_logic')

        return self.handler(user_obj=user_obj, organization=obj) \
               and perm.split('.')[1] in self.permissions


# Handlers
def member_is_admin(user_obj, organization=None):
    person = Person.objects.get(user=user_obj)
    return organization \
           and organization.is_admin(person)


def member_is_admin_not_internal(user_obj, organization=None):
    person = Person.objects.get(user=user_obj)
    return organization \
           and organization.is_admin(person) \
           and not organization.internal


def member_is_member(user_obj, organization=None):
    person = Person.objects.get(user=user_obj)
    return organization \
           and organization.is_member(person)


# Lógicas de permissões
# Organização -> Admin
logic = MemberPermissionLogic(
    member_is_admin,
    ['can_view', 'can_add_event'],
)
add_permission_logic(Organization, logic)

# Organização -> Admin -> Não Interno
logic = MemberPermissionLogic(
    member_is_admin_not_internal,
    ['can_invite'],
)
add_permission_logic(Organization, logic)

# Organização -> Membro
logic = MemberPermissionLogic(
    member_is_member,
    ['can_view', ],
)
add_permission_logic(Organization, logic)

# Organização -> Admin -> membros
logic = MemberPermissionLogic(
    member_is_admin_not_internal,
    ['delete_member', ],
    'organization',
)
add_permission_logic(Member, logic)

# Organização -> Admin -> eventos
logic = MemberPermissionLogic(
    member_is_admin,
    ['delete_event'],
    'organization',
)
add_permission_logic(Event, logic)

logic = MemberPermissionLogic(
    member_is_member,
    ['change_event'],
    'organization',
)
add_permission_logic(Event, logic)
