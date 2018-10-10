import json

from django.conf import settings
from django.utils.formats import localize

from mailer.tasks import send_mail


def notify_admins_postback(transaction, data):
    event = transaction.subscription.event

    body = """
        <br />
        <strong>NOVO POSTBACK:</strong>
        <br /><br />
        <strong>TIPO:</strong> {type_display} ({type})
        <br />
        <strong>Evento:</strong> {event_name} ({event_pk})
        <br />
        <strong>PESSOA:</strong> {person_name}
        <br />
        <strong>E-mail:</strong> {person_email}
        <br />
        <strong>Inscrição:</strong> {sub_pk}
        <br />
        <strong>VALOR (R$):</strong> R$ {amount}
        <br />
        <strong>STATUS:</strong> {status_display} ({status})
        <br />
        <hr >
        <br />
        <strong>Data:</strong>
        <br />    
        <pre><code>{data}</code></pre>
        <br />
    """.format(
        type_display=transaction.get_type_display(),
        type=transaction.type,
        event_name=event.name,
        event_pk=event.pk,
        person_name=transaction.subscription.person.name,
        person_email=transaction.subscription.person.email,
        sub_pk=transaction.subscription.pk,
        amount=localize(transaction.amount),
        status_display=transaction.get_status_display(),
        status=transaction.status,
        data=json.dumps(data),
    )

    send_mail(
        subject="Novo postback: {}".format(event.name),
        body=body,
        to=settings.DEV_ALERT_EMAILS
    )
