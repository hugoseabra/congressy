""" Mailer service. """
from django.template.loader import render_to_string
from .tasks import send_mail


def notify_new_subscription(event, subscription):
    """
    Define a notificação para uma nova inscrição
    """
    person = subscription.person
    local = '{}, {}-{}'.format(
        event.place,
        event.braziliancity.name,
        event.braziliancity.uf
    )

    body = render_to_string('mailer/notify_subscription.html', {
        'gender_article': 'a' if person.gender == 'F' else 'o',
        'person': person,
        'period': event.period,
        'count': subscription.count,
        'date': subscription.created,
        'local': local
    })

    return send_mail.delay(
        subject='Inscrição: {}'.format(event.name),
        body=body,
        to=person.email,
    )
