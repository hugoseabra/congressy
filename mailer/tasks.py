"""
Task to send e-mails
"""
import os

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils import six
from lxml import html


def send_mail(subject, body, to, reply_to=None, attachment_file_path=None):
    """ Envia um email """
    if not to:
        to = []
    elif isinstance(to, six.string_types):
        to = [to]

    if not reply_to:
        reply_to = [settings.CONGRESSY_REPLY_TO]
    elif isinstance(reply_to, six.string_types):
        reply_to = [reply_to]

    body_txt = html.document_fromstring(body).text_content()

    mail = EmailMultiAlternatives(
        subject=subject.strip(),
        body=body_txt,
        to=to,
        reply_to=reply_to
    )

    mail.attach_alternative(body, 'text/html')

    if attachment_file_path:
        if not os.path.isfile(attachment_file_path):
            raise Exception(
                'Aquivo de anexo informado e não'
                ' encontrado: {}'.format(attachment_file_path)
            )

        mail.attach_file(attachment_file_path)

    return mail.send(False)
