from django.core.exceptions import SuspiciousOperation

from gatheros_event.models import Member

USER_CONTEXT_KEYS = (
    'active_organization',
    'active_member_group',
    'organizations',
    'members',
    'superuser',
)


def is_user_context_configured( request ):
    if 'user_context' not in request.session:
        return False

    session_user_context = request.session.get('user_context')

    for key in USER_CONTEXT_KEYS:
        if key not in session_user_context:
            return False

    return True


def get_user_context( request ):
    user_request = UserRequest(request.user)
    if not is_user_context_configured(request):
        return update_user_context(request, None, user_request)

    return user_request


def update_user_context( request, organization=None, user_context=None ):
    if not user_context:
        user_context = UserRequest(request.user)

    if organization:
        user_context.update_active_context(organization)

    request.session.update({'user_context': {
        'active_organization': user_context.active_organization,
        'active_member_group': user_context.active_member_group,
        'organizations': user_context.organizations,
        'members': user_context.members,
        'superuser': user_context.superuser
    }})
    request.session.modified = True

    return user_context


def clean_user_context( request ):
    if 'user_context' in request.session:
        del request.session['user_context']


class UserRequest(object):
    organization = None
    person = None
    logged_user = None
    superuser = False
    organizations = []
    members = []

    # Organização ativa no contexto da sessão do usuário
    active_organization = None
    active_member_group = None

    def __init__( self, user ):
        self.logged_user = user
        self.superuser = user.is_superuser
        self.organization = None
        self.organizations = []
        self.members = []

        self._extract_data_from_logged_user()

    def update_active_context( self, organization ):
        active_org_pks = [org.get('pk') for org in self.organizations]
        active_member_pks = [member.get('pk') for member in self.members]

        if not self.superuser and not hasattr(self.logged_user, 'person'):
            raise SuspiciousOperation(
                'O usuário logado não possui vinculo com pessoa no sistema.'
            )

        try:
            organization.members.get(person=self.person)

            self.organization = organization
            self.active_organization = self.extract_organization_data(
                organization
            )
            self.active_member_group = self.extract_member_data(
                organization.members.get(person=self.person)
            )
        except Member.DoesNotExist:
            raise SuspiciousOperation(
                'Você está tentando entrar em uma organização na qual você não'
                ' é membro.'
            )

        return self

    def _extract_data_from_logged_user( self ):
        if not hasattr(self.logged_user, 'person'):
            return

        self.person = self.logged_user.person

        for member in self.person.members \
                .filter(organization__active=True) \
                .order_by('-organization__internal', 'organization__name'):

            org_data = self.extract_organization_data(member.organization)
            member_data = self.extract_member_data(member)
            self.organizations.append(org_data)
            self.members.append(member_data)

            if not self.active_organization:
                self.active_organization = org_data
                self.organization = member.organization

            if not self.active_member_group:
                self.active_member_group = member_data

    def extract_organization_data( self, organization ):
        return {
            'pk': organization.pk,
            'name': organization.name,
            'internal': organization.internal
        }

    def extract_member_data( self, member ):
        return {
            'pk': member.pk,
            'group_name': member.get_group_display(),
            'group': member.group,
            'organization': self.extract_organization_data(member.organization)
        }
