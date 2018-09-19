from gatheros_subscription.models import Subscription


def subscription_is_checked(subscription_pk):

    try:
        subscription = Subscription.objects.get(pk=subscription_pk)

    except Subscription.DoesNotExist:
        return False

    event = subscription.event

    only_attended = False
    if hasattr(event, 'certificate'):
        only_attended = event.certificate.only_attending_participantes

    if not only_attended:
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
