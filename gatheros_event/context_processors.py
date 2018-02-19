"""
Gatheros Event template context processor
"""
from django.core.exceptions import ObjectDoesNotExist

from gatheros_event.models import Member
from gatheros_subscription.models import Subscription
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

    has_subscriptions = False
    try:
        person = request.user.person
        subs = Subscription.objects.filter(person=person).count()
        has_subscriptions = subs > 0

    except (AttributeError, ObjectDoesNotExist):
        pass

    if not configured and authenticated:
        _account_helper.update_account(request)

    if not _account_helper.is_manager(request):
        return {
            'context_type': 'participant',
            'has_subscriptions': has_subscriptions,
        }

    organization = _account_helper.get_organization(request)
    admins = organization.get_members(group=Member.ADMIN).count()
    organization_unique_admin = admins == 1
    member_unique_organization = request.user.person.members.count() == 1

    return {
        'context_type': 'member',
        'organizations': _account_helper.get_organizations(request),
        'organization': organization,
        'organization_unique_admin': organization_unique_admin,
        'member': _account_helper.get_member(request),
        'member_unique_organization': member_unique_organization,
        'has_subscriptions': has_subscriptions,
    }
