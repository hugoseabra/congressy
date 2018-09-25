from gatheros_subscription.models import Subscription
from attendance.models import AttendanceService

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

    if checkin.attendance_service.checkout_enabled is False:
        if hasattr(checkin, 'checkout') and checkin.checkout is not None:
            return False

    return True


def get_all_attended_in_event(attendance_pk):
    attendance = AttendanceService.objects.get(pk=attendance_pk)

    queryset = Subscription.objects.filter(
        event_id=attendance.event_id,
        checkins__attendance_service__pk=attendance_pk,
        status=Subscription.CONFIRMED_STATUS,
        completed=True, test_subscription=False,
    )

    if attendance.checkout_enabled is False:
        queryset.filter(
            checkins__checkout__isnull=True,
        )

    return queryset