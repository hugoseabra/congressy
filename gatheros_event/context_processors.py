from .helpers import account as _account


def account(request):
    """
    Adiciona informações da conta no contexto
    """

    if not request.user.is_authenticated:
        return {}

    return {
        'organizations': _account.get_organizations(request),
        'organization': _account.get_organization(request),
        'member': _account.get_member(request),
    }
