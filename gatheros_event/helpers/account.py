"""
Helper para configuração de contexto de usuário mediante sessão e organização
ativa do usuário na sessão.
"""
from django.core.exceptions import SuspiciousOperation

from gatheros_event.models import Organization, Person


def is_configured(request):
    """Verifica se contexto de sessão está configurada."""

    if hasattr(request, 'cached_context_participant') \
            and request.cached_context_participant is True:
        return True

    has_account = 'account' in request.session
    if has_account:
        return bool(request.session['account']) is True

    clean_account(request)
    return False


def is_participant(request):
    if hasattr(request, 'cached_context_participant'):
        return getattr(request, 'cached_context_participant', False)

    return False


def get_organization(request):
    """Retorna a organização ativa na sessão."""
    if not hasattr(request, 'cached_organization'):
        account = request.session.get('account')
        try:
            org = Organization.objects.get(pk=account.get('organization'))
            request.cached_organization = org

        except Organization.DoesNotExist:
            return None

    return request.cached_organization


def get_organizations(request):
    """
    Retorna as organizações do usuário autenticado.

    :param request: Instância de HttpRequest
    :return: list
    """
    if not hasattr(request, 'cached_organizations'):
        account = request.session.get('account')
        request.cached_organizations = list(
            Organization.objects.filter(
                pk__in=account.get('organizations')
            ).order_by('-internal', 'name')
        )

    return request.cached_organizations


def get_member(request):
    """
    Retorna informação sobre o membro do usuário na organização ativa da sessão

    :param request:
    :return:
    """
    if not hasattr(request, 'cached_member'):
        try:
            request.cached_member = get_organization(request).members.get(
                person=request.user.person
            )

        except Organization.DoesNotExist:
            return None

    return request.cached_member


def set_organization(request, organization):
    """
    Atualiza a organização ativa na sessão

    :param request:
    :param organization: int
    Pk da organização ativa da sessão
    :return:
    """
    clean_cache(request)

    if isinstance(organization, Organization):
        organization = organization.pk

    request.session['account'].update({'organization': organization})
    request.session.modified = True


def update_account(request, organization=None):
    """
    Atualiza as informações das organizações e marca a organização principal
    como ativa na sessao

    :param request:
    :param organization: int
    Pk da organização ativa da sessão
    :return:
    """
    if is_participant(request):
        return

    if not is_configured(request):
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

        member = person.members \
            .filter(organization__active=True) \
            .order_by('-organization__internal', 'organization__name') \
            .first()

        if not member:
            request.cached_context_participant = True
        else:
            organization = member.organization

    if is_participant(request):
        return

    set_organization(request, organization)

    if request.session['account'].get('organizations') is None:
        clean_cache(request)

        # Definindo todas organizações na sessão
        organizations = Organization.objects.filter(
            members__person=request.user.person
        )

        request.session['account'].update({
            'organizations': [o.pk for o in organizations]
        })
        request.session.modified = True
        clean_cache(request)


def clean_account(request):
    """
    Remove as informações de conta da sessão

    :param request:
    :return:
    """
    if 'account' in request.session:
        del request.session['account']

    clean_cache(request)


def clean_cache(request):
    """Limpa cache de contexto de organização da sessão."""
    if hasattr(request, 'cached_context_type'):
        del request.cached_context_participant

    if hasattr(request, 'cached_organizations'):
        del request.cached_organizations

    if hasattr(request, 'cached_organization'):
        del request.cached_organization

    if hasattr(request, 'cached_member'):
        del request.cached_member
