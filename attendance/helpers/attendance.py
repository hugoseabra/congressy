from gatheros_subscription.models import Subscription


def subscription_is_checked(subscription_pk, event_pk):
    queryset = Subscription.objects.filter(
        pk=subscription_pk,
        event_id=event_pk)

    queryset = queryset.filter(
        checkins__isnull=False,
    ).count()

    return queryset > 0
