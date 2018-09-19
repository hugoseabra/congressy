from gatheros_subscription.models import Subscription
from django.core.exceptions import ObjectDoesNotExist


def subscription_is_checked(subscription_pk):
    only_attending = False
    try:
        subscription = Subscription.objects.get(
            pk=subscription_pk)

    except ObjectDoesNotExist:
        return False

    event = subscription.event

    if hasattr(event, 'certificate'):
        only_attending = event.certificate.only_attending_participantes

    if not only_attending:
        return True

    checkin = subscription.checkins.filter(
        attendance_service__with_certificate=True
    ).last()

    if not checkin:
        return False

    if checkin.attendance_service.checkin_only:
        if hasattr(checkin, 'checkout') and checkin.checkout is not None:
            return False

    return True
