from cgsy_video import synchronizer
from cgsy_video.synchronizer import (
    get_user_data,
    get_user,
    get_namespace,
    get_namespace_data,
    get_project,
    get_project_data,
    get_subscriber_data,
    get_subscriber,
)
from gatheros_event.models import Event
from gatheros_subscription.models import Subscription


def sync_event_user(event_pk):
    try:
        event = Event.objects.get(pk=event_pk)
    except Event.DoesNotExist:
        return

    user_data = get_user_data(event)
    event_user = get_user(event)

    for k, v in user_data.items():
        setattr(event_user, k, v)

    event_user.save()

    return event_user


def sync_namespace(event_pk):
    try:
        event = Event.objects.get(pk=event_pk)
    except Event.DoesNotExist:
        return

    event_user = get_user(event)
    namespace = get_namespace(event, event_user)
    namespace_data = get_namespace_data(event, event_user.pk)

    for k, v in namespace_data.items():
        setattr(namespace, k, v)

    namespace.save()

    return namespace


def sync_project(event_pk):
    try:
        event = Event.objects.get(pk=event_pk)
    except Event.DoesNotExist:
        return

    event_user = get_user(event)
    namespace = get_namespace(event, event_user)
    project = get_project(event, event_user, namespace)
    project_data = get_project_data(event, namespace.pk)

    for k, v in project_data.items():
        setattr(project, k, v)

    project.save()

    return project


def create_video_config(event_pk):
    try:
        event = Event.objects.get(pk=event_pk)
    except Event.DoesNotExist:
        return

    return synchronizer.get_event_video_config(event)


def sync_subscriber(subscription_pk):
    try:
        subscription = Subscription.objects.get(pk=subscription_pk)
    except Subscription.DoesNotExist:
        return

    subscriber = get_subscriber(subscription)
    if not subscriber:
        # Possible deleted
        return

    sub_data = get_subscriber_data(subscription, subscriber.project)

    for k, v in sub_data.items():
        setattr(subscriber, k, v)

    subscriber.save()

    return subscriber
