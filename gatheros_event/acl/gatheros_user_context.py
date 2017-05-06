from django.core.exceptions import ImproperlyConfigured, SuspiciousOperation
from django.shortcuts import get_object_or_404

from gatheros_event.models import Organization


def get_user_context( request ):
    return UserRequest(request)


def update_user_context( request, organization_pk=None ):
    return UserRequest.update(request, organization_pk)


class UserRequest(object):
    superuser = False
    person = None
    organization = None
    organizations = []
    members = []

    """
    User nome do campo ou algum método e o nome do atributo a ser gravado:
    <field_or_method>.<attribute_name>

    Se <attribute_name> não for informado, o nome do campo será usado como
     atributo.
    """
    organization_dict_fields = ['pk', 'name', 'internal']
    member_dict_fields = ['pk', 'group', 'get_group_display.name']

    # Organização ativa no contexto da sessão do usuário
    active_organization = None
    active_member_group = None

    def __init__( self, request, organization=None ):
        self.session = request.session
        self.logged_user = request.user
        self.superuser = request.user.is_superuser
        self.organization = organization
        self.organizations = []
        self.members = []

        self._extract_data_from_logged_user()
        if organization:
            self._update_active_context(organization)

    @staticmethod
    def is_event_manager( request ):
        """
        Membro de organização pode não ser organizador de evento e poder
        administrador eventos de outras pessoas.
        """
        user_request = UserRequest(request)
        return user_request.person is not None and len(user_request.members) > 0

    @staticmethod
    def update( request, organization_pk=None ):
        organization = None
        if organization_pk:
            organization = get_object_or_404(Organization, pk=organization_pk)

        return UserRequest(request, organization)

    @staticmethod
    def is_configured( request ):
        return hasattr(request.session, 'user_context')

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

            if not self.active_member_group:
                self.active_member_group = member_data

        self._update_session()

    def extract_organization_data( self, organization ):
        return self._extract_data_from_model(
            organization,
            self.organization_dict_fields
        )

    def extract_member_data( self, member ):
        member_data = self._extract_data_from_model(
            member,
            self.member_dict_fields
        )
        member_data.update({
            'organization': self._extract_data_from_model(
                member.organization,
                self.organization_dict_fields
            )}
        )
        return member_data

    def _update_active_context( self, organization ):
        active_org_pks = [org.get('pk') for org in self.organizations]
        active_member_pks = [member.get('pk') for member in self.members]

        if not self.superuser and not hasattr(self.logged_user, 'person'):
            raise SuspiciousOperation(
                'O usuário logado não possui vinculo com pessoa no sistema.'
            )

        member = organization.members.get(person=self.person)

        # Se não é super usuário e não pertence à organização
        if not self.superuser \
                and organization.pk not in active_org_pks \
                and member.pk not in active_member_pks:
            raise SuspiciousOperation(
                'Você está tentando entrar em uma organização na qual você não'
                ' é membro.'
            )

        self.active_organization = self.extract_organization_data(organization)
        self.active_member_group = self.extract_member_data(
            organization.members.get(person=self.person)
        )

        self._update_session()

    def _update_session( self ):
        self.session.update({'user_context': {
            'active_organization': self.active_organization,
            'active_member_group': self.active_member_group,
            'organizations': self.organizations,
            'members': self.members,
            'superuser': self.superuser
        }})

    def _extract_data_from_model( self, model_instance, fields ):

        def get_value( attr ):
            if not hasattr(model_instance, attr):
                raise ImproperlyConfigured(
                    'Model \'{}\' não possui o atributo \'{}\''.format(
                        model_instance._meta.verbose_name,
                        attr
                    )
                )

            attr_value = getattr(model_instance, attr)
            if callable(getattr(model_instance, attr)):
                return attr_value()

            return attr_value

        data = {}
        for field_name in fields:
            if '.' not in field_name:
                data.update({field_name: get_value(field_name)})
                continue
            attribute, name = field_name.split('.')

            if not attribute or not name:
                raise ImproperlyConfigured(
                    'Configuração de campos a ser resgatados do Model {}'
                    'estão incorretas. Valor incorreto: {}'.format(
                        model_instance._meta.verbose_name,
                        field_name
                    )
                )
            data.update({name: get_value(attribute)})

        return data
