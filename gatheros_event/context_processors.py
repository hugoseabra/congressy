"""
Gatheros Event template context processor
"""
from django.core.exceptions import ObjectDoesNotExist

from .helpers import account as _account_helper

from gatheros_subscription.models import Subscription

def account(request):
    """
    Adiciona informações da conta no contexto
    """
    if hasattr(request, 'current_app') and request.current_app == 'admin':
        return {}

    configured = _account_helper.is_configured(request)
    authenticated = request.user.is_authenticated

    has_subscriptions = False

    try:
        person = request.user.person
        subs = Subscription.objects.filter(person=person).count()
        has_subscriptions = subs > 0

    except (AttributeError, ObjectDoesNotExist):
        pass

    if not configured and not authenticated:
        return {}

    if not configured and authenticated:
        _account_helper.update_account(request)

    if not _account_helper.is_manager(request):
        return {
            'context_type': 'participant',
            'has_subscriptions': has_subscriptions,
        }

    return {
        'context_type': 'member',
        'organizations': _account_helper.get_organizations(request),
        'organization': _account_helper.get_organization(request),
        'member': _account_helper.get_member(request),
        'has_subscriptions': has_subscriptions,
    }
