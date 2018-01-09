""" Mailer service. """
from django.conf import settings
from django.template.loader import render_to_string
from .tasks import send_mail


def notify_new_subscription(event, subscription):
    """
    Define a notificação para uma nova inscrição
    """
    person = subscription.person
    local = '{}'.format(
        event.place,
    )

    # @TODO set event.date_start to period
    body = render_to_string('mailer/notify_subscription.html', {
        'gender_article': 'a' if person.gender == 'F' else 'o',
        'person': person,
        'period': event.date_start,
        'count': subscription.count,
        'date': subscription.created,
        'local': local
    })

    if settings.DEBUG:
        return send_mail(
            subject='Inscrição: {}'.format(event.name),
            body=body,
            to=person.email
        )

    return send_mail.delay(
        subject='Inscrição: {}'.format(event.name),
        body=body,
        to=person.email,
    )


def notify_new_user_and_subscription(event, subscription, link):
    """
    Define a notificação para uma nova inscrição com novo user
    """
    person = subscription.person

    local = '{}'.format(
        event.place,
    )

    # @TODO set event.date_start to period
    body = render_to_string('mailer/notify_user_and_subscription.html', {
        'event': event,
        'gender_article': 'a' if person.gender == 'F' else 'o',
        'person': person,
        'period': event.date_start,
        'count': subscription.count,
        'complete_sign_up_link': link,
        'date': subscription.created,
        'local': local
    })

    if settings.DEBUG:
        return send_mail(
            subject='Inscrição: {}'.format(event.name),
            body=body,
            to=person.email
        )

    return send_mail.delay(
        subject='Inscrição: {}'.format(event.name),
        body=body,
        to=person.email,
    )
