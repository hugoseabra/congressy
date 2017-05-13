from .helpers import account as _account_helper


def account(request):
    """
    Adiciona informações da conta no contexto
    """

    if not request.user.is_authenticated \
            or not _account_helper.is_configured():
        return {}

    return {
        'organizations': _account_helper.get_organizations(request),
        'organization': _account_helper.get_organization(request),
        'member': _account_helper.get_member(request),
    }
