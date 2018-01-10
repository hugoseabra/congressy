"""
Task to send e-mails
"""

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.utils import six
from lxml import html


def send_mail(subject, body, to):
    """ Envia um email """
    if not to:
        to = []
    elif isinstance(to, six.string_types):
        to = [to]

    body_txt = html.document_fromstring(body).text_content()

    mail = EmailMultiAlternatives(
        subject=subject.strip(),
        body=body_txt,
        to=to,
        reply_to=[settings.CONGRESSY_REPLY_TO]
    )

    mail.attach_alternative(body, 'text/html')

    return mail.send(False)


def send_mass_mail(subject, body, to):
    """
    Envia diversos e-mails, abrindo apenas uma conexão.

    :param self:
        Self instance assumed by @app.task
    :param subject:
        E-mail subject
    :param body:
        E-mail html body
    :param to:
        E-mail addresses to send the message
    :return:
        Number of sent messages.
    """

    if not isinstance(to, list) and not isinstance(to, tuple):
        raise TypeError('"to" argument must be a list or tuple')

    body_txt = html.document_fromstring(body).text_content()
    subject = subject.strip()

    connection = get_connection()

    messages = []
    for address in to:
        message = EmailMultiAlternatives(
            subject=subject,
            body=body_txt,
            to=address,
            from_email=settings.CONGRESSY_EMAIL_SENDER,
            reply_to=settings.CONGRESSY_REPLY_TO,
            connection=connection
        )
        message.attach_alternative(body, 'text/html')
        messages.append(message)

    return connection.send_messages(messages)
