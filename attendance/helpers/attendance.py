from gatheros_subscription.models import Subscription
from attendance.models import AttendanceService


def subscription_is_checked(subscription_pk, event_pk):
    subscription = Subscription.objects.get(
        pk=subscription_pk,
        event_id=event_pk)

    queryset = subscription.checkins.all()

    for item in queryset:
        if item.attendance_service.checkin_only:
            if item.checkin.checkout:
                return False

        if not item.attendance_service.with_certificate:
                return False

        return True
