"""
Helper para configuração de contexto de usuário mediante sessão e organização
ativa do usuário na sessão.
"""
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User

from gatheros_event.models import Organization, Person


def is_eligible(request):
    """
    Verifica se instância de usuario é elegível para processar o contexto:
    - Se `RequestHttp` possui atributo de usuário
    - Se usuário do atributo é uma instânica de
    `django.contrib.auth.models.User`
    - Se usário está logado.
    """
    if not hasattr(request, 'user'):
        return False

    user = request.user

    # Usuário com objeto correto e autenticado
    user_state_ok = isinstance(user, User) and user.is_authenticated()

    if not user_state_ok:
        return False

    try:
        # Se há pessoa
        person = user.person

    except Person.DoesNotExist:
        return False

    else:
        return person is not None


def is_configured(request):
    """ Verifica se contexto de sessão está configurada. """

    # Se usuário não é Organizador de evento, está tudo certo.
    if hasattr(request, 'cached_context_is_manager') \
            and request.cached_context_is_manager is False:
        return True

    has_account = 'account' in request.session
    if has_account:
        return bool(request.session['account']) is True

    clean_account(request)
    return False


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


def fetch_user_members(request):
    """ Resgata membros vinculados ao usuário logado. """
    try:
        return request.user.person.members.filter(
            organization__active=True,
            active=True
        ).order_by('-organization__internal', 'organization__name')

    except ObjectDoesNotExist:
        return None


def is_manager(request):
    """
    Verifica se o usuário logado é Organizador de evento.

    :param request: django.http.HttpRequest
    :return: Boolean
        Se False, significa que o usuário é apenas um participante e não possui
        permissões de acessar áreas de Organizador de evento.
    """

    if hasattr(request, 'cache_user_is_member'):
        return request.cache_user_is_member

    if not is_eligible(request):
        return False

    members = fetch_user_members(request)
    is_member = members is not None and members.count() > 0

    request.cache_user_is_member = is_member
    return is_member


def clean_account(request):
    """
    Remove as informações de conta da sessão

    :param request:
    :return:
    """
    if 'account' in request.session:
        del request.session['account']

    clean_cache(request)


def get_organization(request):
    """Retorna a organização ativa na sessão."""

    if not is_manager(request):
        return None

    account = request.session.get('account')
    is_dict = isinstance(account, dict)

    # Solicitação de resgate de organização aconteceu antes da atualização
    if not is_dict or is_dict and account.get('organization') is None:
        return None

    if not hasattr(request, 'cached_organization'):
        try:
            org = Organization.objects.get(
                pk=account.get('organization'),
                active=True
            )
            request.cached_organization = org

        # Para caso a organização esteja desativada.
        except Organization.DoesNotExist:
            return None

    return request.cached_organization


def get_organizations(request):
    """
    Retorna as organizações do usuário autenticado.

    :param request: Instância de HttpRequest
    :return: list
    """

    if not is_manager(request):
        return []

    if not hasattr(request, 'cached_organizations'):
        account = request.session.get('account')

        # Solicitação de resgate de organizações aconteceu antes da atualização
        if not account:
            return []

        request.cached_organizations = list(
            Organization.objects.filter(
                pk__in=account.get('organizations'),
                active=True
            ).order_by('-internal', 'name')
        )

    return request.cached_organizations


def get_member(request):
    """
    Retorna informação sobre o membro do usuário na organização ativa da sessão

    :param request:
    :return:
    """

    if not is_manager(request):
        return None

    if not hasattr(request, 'cached_member'):
        organization = get_organization(request)
        request.cached_member = organization.get_member(request.user)

    return request.cached_member


def set_active_organization(request, organization):
    """
    Define a organização ativa na sessão.

    :param request:
    :param organization: int | Organization instance
        PK ou instância da organização a ser ativa na sessão.
    :return:
    """

    clean_cache(request)

    # Se usuário não é Organizador ou não membro da organização, não será
    # possível ativar.
    if not is_manager(request) or not organization.is_member(request.user):
        return

    if isinstance(organization, Organization):
        organization = organization.pk

    request.session['account'].update({'organization': organization})
    request.session.modified = True


def update_account(request, organization=None, force=False):
    """
    Atualiza as informações das organizações e marca a organização principal
    como ativa na sessao

    :param request:
    :param organization: int
    Pk da organização ativa da sessão
    :param force: Força a atualização de organizações
    :return: None
    """

    # Primeiro verifica se é elegível
    if not is_manager(request):
        return

    if not is_configured(request):
        request.session['account'] = {}

    # Tenta definir a organização se não houver
    if organization is None:
        member = fetch_user_members(request).first()

        # Atualizar com a organização do primeiro membro da lista.
        organization = member.organization

    # Tentativa de registro de organização de contexto de um não Organizador
    elif not is_manager(request):
        return

    # Se há o parâmetro de organização e usuário logado não é membro.
    elif organization and not organization.is_member(request.user):
        return

    has_account = 'account' in request.session
    account = request.session['account'] if has_account else {}
    no_orgs = account is not None and account.get('organizations') is None

    if force or no_orgs:
        # Começa do zero
        clean_cache(request)

        # Persistindo PKs de organizações na sessão
        request.session['account'].update({
            'organizations': [
                m.organization.pk for m in fetch_user_members(request)
            ]
        })
        request.session.modified = True

    # # Busca instâncias de organização de acordo com o request
    # organizations = get_organizations(request)
    #
    # # Se a organização do contexto não foi carregada, carrega a primeira
    # if organization not in organizations:
    #     organization = organizations[0]

    set_active_organization(request, organization)
