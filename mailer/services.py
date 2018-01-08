""" Mailer service. """
from django.template.loader import render_to_string
from .tasks import send_mail


def notify_subscription(event, subscription):
    """
    Define a notificação para uma nova inscrição
    """
    person = subscription.person
    local = '{}, {}-{}'.format(
        event.place,
        event.braziliancity.name,
        event.braziliancity.uf
    )

    subject = render_to_string('mailer/email_subject.txt', {
        'event': event.name
    })
    body = render_to_string('mailer/email_body.html', {
        'gender_article': 'a' if person.gender == 'F' else 'o',
        'person': person,
        'period': event.period,
        'count': subscription.count,
        'date': subscription.created,
        'local': local
    })

    return send_mail.delay(
        subject=subject.strip(),
        body=body,
        to=person.email,
    )
