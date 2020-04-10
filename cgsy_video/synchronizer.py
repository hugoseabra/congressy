from django.conf import settings

from cgsy_video.models import VideoConfig
from congressy import Congressy
from congressy.exceptions import CongressyAPIException


def get_congressy_client(api_key):
    kwargs = {
        'api_key': api_key,
        'api_key_type': 'Token'
    }

    if settings.DEBUG is True:
        kwargs.update({'host': settings.CGSY_VIDEOS_API_URL})

    return Congressy(**kwargs)


def get_user_data(event):
    org = event.organization

    username = '{}-{}'.format(org.slug, org.pk)

    return {
        'username': username[0:29],
        'first_name': org.name[0:29],
        'last_name': str(org.pk),
    }


def get_user(event):
    congressy = get_congressy_client(settings.CGSY_VIDEOS_API_ADMIN_TOKEN, )

    user_class = congressy.video.user

    user_data = get_user_data(event)

    try:
        user = user_class.get_manager().get(username=user_data['username'])
    except CongressyAPIException as e:
        if e.status != 404:
            raise e

        user = user_class(**user_data)

    if user.valid() is False:
        raise Exception(user.errors)

    user.save()

    return user


def get_namespace_data(event, event_user_pk):
    return {
        'name': 'Hotsite: {}'.format(event.name),
        'slug': event.slug,
        'user': event_user_pk,
        'external_id': str(event.pk),
    }


def get_namespace(event, event_user):
    congressy = get_congressy_client(event_user.auth_token)

    namespace_class = congressy.video.namespace
    namespace_data = get_namespace_data(event=event,
                                        event_user_pk=event_user.pk)
    namespaces = namespace_class.get_manager().get_all()
    namespace = namespaces[0] if namespaces else None

    if namespace is None:
        namespace = namespace_class(**namespace_data)
    else:
        for k, v in namespace_data.items():
            setattr(namespace, k, v)

    if namespace.valid() is False:
        raise Exception(namespace.errors)

    namespace.save()

    return namespace


def get_project_data(event, namespace_pk):
    return {
        'name': event.name,
        'namespace': str(namespace_pk),
        'active': True,
    }


def get_project(event, event_user, namespace):
    congressy = get_congressy_client(event_user.auth_token)

    project_class = congressy.video.project
    project_data = get_project_data(event=event, namespace_pk=namespace.pk)
    projects = project_class.get_manager().get_all()
    project = projects[0] if projects else None

    if project is None:
        project = project_class(**project_data)
    else:
        for k, v in project_data.items():
            setattr(project, k, v)

    if project.valid() is False:
        raise Exception(project.errors)

    project.save()

    return project


def get_event_video_config(event):
    if hasattr(event, 'video_config') and event.video_config:
        return event.video_config

    event_user = get_user(event)
    namespace = get_namespace(event, event_user)
    project = get_project(event, event_user, namespace)
    config = VideoConfig(
        event=event,
        token=event_user.auth_token,
        project_pk=project.pk,
    )
    config.save()

    return config


def get_subscriber_data(subscription, project_pk):
    return {
        'external_id': str(subscription.pk),
        'project': str(project_pk),
        'restriction_keys': str(subscription.lot_id),
        'verified': True,
        'subscription_metadata': {
            'lot': subscription.lot_id,
        },
    }


def get_subscriber(subscription):
    event = subscription.event
    event_user = get_user(event)
    namespace = get_namespace(event, event_user)
    project = get_project(event, event_user, namespace)

    congressy = get_congressy_client(event_user.auth_token)
    subscriber_class = congressy.video.subscriber
    subscriber_data = get_subscriber_data(
        subscription=subscription,
        project_pk=project.pk,
    )
    subs = subscriber_class.get_manager().get_all(
        external_id=str(subscription.pk),
        project=str(project.pk),
    )
    sub = subs[0] if subs else None

    not_confirmed = subscription.confirmed is False
    test_subscription = subscription.test_subscription is True
    skip = not_confirmed is True or test_subscription is True

    if skip is True:
        if sub:
            sub.delete()

        return None

    if sub is None:
        sub = subscriber_class(**subscriber_data)
    else:
        for k, v in subscriber_data.items():
            setattr(sub, k, v)

    if sub.valid() is False:
        raise Exception(sub.errors)

    sub.save()

    return sub
