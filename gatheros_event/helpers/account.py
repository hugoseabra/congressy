from django.core.exceptions import SuspiciousOperation

from gatheros_event.models import Organization, Person


def get_organization(request):
    if not hasattr(request, '_cached_organization'):
        account = request.session.get('account')
        try:
            request._cached_organization = Organization.objects \
                .get(pk=account.get('organization'))
        except Organization.DoesNotExist:
            return None
    return request._cached_organization


def get_organizations(request):
    """
    Retorna a organização ativa na sessão

    :param request:
    :return:
    """
    if not hasattr(request, '_cached_organizations'):
        account = request.session.get('account')
        request._cached_organizations = list(
            Organization.objects.filter(pk__in=account.get('organizations'))
        )
    return request._cached_organizations


def get_member(request):
    """
    Retorna informação sobre o membro do usuário na organização ativa da sessão

    :param request:
    :return:
    """
    if not hasattr(request, '_cached_member'):
        try:
            request._cached_member = get_organization(request).members \
                .get(person=request.user.person)
        except Organization.DoesNotExist:
            return None
    return request._cached_member


def set_organization(request, organization):
    """
    Atualiza a organização ativa na sessão

    :param request:
    :param organization: int
    Pk da organização ativa da sessão
    :return:
    """
    if hasattr(request, '_cached_organization'):
        del request._cached_organization

    if hasattr(request, '_cached_member'):
        del request._cached_member

    if isinstance(organization, Organization):
        organization = organization.pk

    request.session['account'].update({'organization': organization})


def update_session_account(request, organization=None):
    """
    Atualiza as informações das organizações e marca a organização principal
    como ativa na sessao

    :param request:
    :param organization: int
    Pk da organização ativa da sessão
    :return:
    """
    if not hasattr(request.session, 'account'):
        request.session['account'] = {}

    # Definindo a organização ativa na sessão
    if organization is None:
        # Tenta definir a organização se não houver
        try:
            person = request.user.person
        except Person.DoesNotExist:
            raise SuspiciousOperation(
                'Usuário %s não está vinculado a uma pessoa.' % request.user
            )
            # @todo regra para usuários sem pessoa vinculada

        member = person.members \
            .filter(organization__active=True) \
            .order_by('-organization__internal', 'organization__name') \
            .first()

        # @todo verificar regra se algum momento pode usuário sem organização
        organization = member.organization

    set_organization(request, organization)

    # Definindo todas organizações na sessão
    organizations = Organization.objects.filter(
        members__person=request.user.person
    )

    request.session['account'].update({
        'organizations': [o.pk for o in organizations]
    })


def clean_session_account(request):
    """
    Remove as informações de conta da sessão

    :param request:
    :return:
    """
    if 'account' in request.session:
        del request.session['account']

    if hasattr(request, '_cached_organizations'):
        del request._cached_organizations

    if hasattr(request, '_cached_organization'):
        del request._cached_organization

    if hasattr(request, '_cached_member'):
        del request._cached_member
