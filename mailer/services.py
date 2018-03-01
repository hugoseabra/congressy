""" Mailer service. """
import absoluteuri
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

CELERY = False

if settings.DEBUG:
    from .tasks import send_mail
else:
    try:
        from .worker import send_mail

        CELERY = True
    except ImportError:
        from .tasks import send_mail


def notify_new_subscription(event, subscription):
    """
    Define a notificação para uma nova inscrição
    """
    person = subscription.person

    # local = '{}'.format(
    #     event.place,
    # )

    event_url = absoluteuri.reverse(
        'public:hotsite',
        kwargs={
            'slug': event.slug,
        }
    )

    # @TODO set event.date_start to period
    body = render_to_string('mailer/notify_subscription.html', {
        # 'gender_article': 'a' if person.gender == 'F' else 'o',
        'gender_article': 'o(a)',
        'person': person,
        'event': event,
        'event_url': event_url,
        'period': event.date_start,
        # 'count': subscription.count,
        'date': subscription.created,
        # 'local': local
    })

    if CELERY:
        return send_mail.delay(
            subject='Inscrição: {}'.format(event.name),
            body=body,
            to=person.email,
        )

    return send_mail(
        subject='Inscrição: {}'.format(event.name),
        body=body,
        to=person.email
    )


def notify_new_user_and_subscription(event, subscription):
    """
    Define a notificação para uma nova inscrição com novo user
    """
    person = subscription.person

    event_url = absoluteuri.reverse(
        'public:hotsite',
        kwargs={
            'slug': event.slug,
        }
    )

    user = person.user
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    password_reset_url = absoluteuri.reverse(
        'password_reset_confirm',
        kwargs={
            'uidb64': uid,
            'token': token,
        }
    )

    # @TODO set event.date_start to period
    body = render_to_string('mailer/notify_user_and_subscription.html', {
        'password_reset_url': password_reset_url,
        'event': event,
        'event_url': event_url,
        # 'gender_article': 'a' if person.gender == 'F' else 'o',
        'person': person,
        'period': event.date_start,
        'count': subscription.count,
        'date': subscription.created,
    })

    if CELERY:
        return send_mail.delay(
            subject='Inscrição: {}'.format(event.name),
            body=body,
            to=person.email,
        )

    return send_mail(
        subject='Inscrição: {}'.format(event.name),
        body=body,
        to=person.email
    )


def notify_invite(organization, link, invitator, invited_person, email):
    """
    Define a notificação para um novo convite
    """

    body = render_to_string('mailer/notify_invitation.html', {
        'organizacao': organization,
        'hospedeiro': invitator,
        'convidado': invited_person,
        'link': link,
    })

    if CELERY:
        return send_mail.delay(
            subject='Convite: {}'.format(organization),
            body=body,
            to=email,
        )

    return send_mail(
        subject='Convite: {}'.format(organization),
        body=body,
        to=email,
    )


def notify_new_user(context):
    """
    Define a notificação para um usuario na plataforma.
    """

    body = render_to_string('mailer/account_confirmation_email.html',
                            context=context)

    subject = 'Confirmação de cadastro na {0}'.format(context['site_name'])

    if CELERY:
        return send_mail.delay(
            subject=subject,
            body=body,
            to=context['email'],
        )

    return send_mail(
        subject=subject,
        body=body,
        to=context['email'],
    )


def notify_new_partner(context):
    """
    Define a notificação para um novo parceiro na plataforma.
    """

    body = render_to_string('mailer/notify_partner_registration_email.html',
                            context=context)

    subject = 'Cadastro de parceria na  {0}'.format(context['site_name'])

    if CELERY:
        return send_mail.delay(
            subject=subject,
            body=body,
            to=context['partner_email'],
        )

    return send_mail(
        subject=subject,
        body=body,
        to=context['partner_email'],
    )


def notify_partner_contract(context):
    """
    Define a notificação para um parceiro quando o mesmo é vinculado a um
    evento.
    """

    subject = 'Parceria Congressy: Vinculado ao evento {0}'.format(context[
                                                                    'event'])

    body = render_to_string('mailer/notify_partner_contract_email.html',
                            context=context)

    if CELERY:
        return send_mail.delay(
            subject=subject,
            body=body,
            to=context['partner_email'],
        )

    return send_mail(
        subject=subject,
        body=body,
        to=context['partner_email'],
    )


def notify_new_partner_internal(context):
    """
    Define a notificação interna para o comercial no evento de cadastro um novo
    parceiro na plataforma.
    """

    body = render_to_string(
        'mailer/notify_partner_registration_internal_email.html',
        context=context)

    subject = 'Novo parceiro cadastrado: {0}'.format(context['partner_name'])

    if CELERY:
        return send_mail.delay(
            subject=subject,
            body=body,
            to=settings.SALES_ALERT_EMAILS,
        )

    return send_mail(
        subject=subject,
        body=body,
        to=settings.SALES_ALERT_EMAILS,
    )


def notify_reset_password(context):
    """
    Define a notificação para um usuario na plataforma.
    """

    body = render_to_string('mailer/password_reset_email.html',
                            context=context)

    subject = 'Redefina sua senha na {0}'.format(context['site_name'])

    if CELERY:
        return send_mail.delay(
            subject=subject,
            body=body,
            to=context['email'],
        )

    return send_mail(
        subject=subject,
        body=body,
        to=context['email'],
    )


def notify_set_password(context):
    """
    Define a notificação para um usuario na plataforma.
    """

    body = render_to_string('mailer/password_set_email.html',
                            context=context)

    subject = 'Defina sua senha na {0}'.format(context['site_name'])

    if CELERY:
        return send_mail.delay(
            subject=subject,
            body=body,
            to=context['email'],
        )

    return send_mail(
        subject=subject,
        body=body,
        to=context['email'],
    )


def notify_new_event(event):
    """ Notifica área de vendas quando se cria novo evento. """

    link = absoluteuri.reverse(
        'public:hotsite',
        kwargs={
            'slug': event.slug,
        }
    )

    body = render_to_string(
        template_name='mailer/notify_new_event.html',
        context={
            'event': event,
            'link': link
        }
    )

    if CELERY:
        send_mail.delay(
            body=body,
            subject="Novo evento: {}".format(event.name),
            to=settings.SALES_ALERT_EMAILS
        )

    send_mail(
        body=body,
        subject="Novo evento: {}".format(event.name),
        to=settings.SALES_ALERT_EMAILS
    )
