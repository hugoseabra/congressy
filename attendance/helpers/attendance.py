from attendance.models import AttendanceService
from gatheros_subscription.models import Subscription


def subscription_has_certificate(subscription_pk):
    try:
        subscription = Subscription.objects.all_completed().get(
            pk=subscription_pk,
            event__published=True,
            status=Subscription.CONFIRMED_STATUS,
        )

    except Subscription.DoesNotExist:
        return False

    event = subscription.event

    if event.finished is False:
        return False

    if event.has_certificate_config is False \
            or event.feature_configuration.feature_certificate is False:
        return False

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

    if checkin.attendance_service.checkout_enabled is False:
        if hasattr(checkin, 'checkout') and checkin.checkout is not None:
            return False

    return True


def subscription_is_checked(subscription_pk):
    try:
        subscription = Subscription.objects.get(pk=subscription_pk)

    except Subscription.DoesNotExist:
        return False

    checkin = subscription.checkins.last()

    if not checkin:
        return False

    if checkin.attendance_service.checkout_enabled is False:
        if hasattr(checkin, 'checkout') and checkin.checkout is not None:
            return False

    return True


def get_all_attended_in_event(attendance_pk):
    attendance = AttendanceService.objects.get(pk=attendance_pk)

    queryset = Subscription.objects.all_completed().filter(
        event_id=attendance.event_id,
        checkins__attendance_service__pk=attendance_pk,
        status=Subscription.CONFIRMED_STATUS,
    )

    if attendance.checkout_enabled is False:
        queryset.filter(
            checkins__checkout__isnull=True,
        )

    return queryset
