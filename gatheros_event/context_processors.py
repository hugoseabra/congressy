"""
Gatheros Event template context processor
"""
from .helpers import account as _account_helper


def account(request):
    """
    Adiciona informações da conta no contexto
    """
    if hasattr(request, 'current_app') and request.current_app == 'admin':
        return {}

    configured = _account_helper.is_configured(request)
    authenticated = request.user.is_authenticated

    if not configured and not authenticated:
        return {}

    if not configured and authenticated:
        _account_helper.update_account(request)

    if not _account_helper.is_manager(request):
        return {'context_type': 'participant'}

    return {
        'context_type': 'member',
        'organizations': _account_helper.get_organizations(request),
        'organization': _account_helper.get_organization(request),
        'member': _account_helper.get_member(request),
    }
