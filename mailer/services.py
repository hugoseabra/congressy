""" Mailer service. """
import absoluteuri
from django.conf import settings
from django.template.loader import render_to_string

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


def notify_new_user_and_subscription(event, subscription, link):
    """
    Define a notificação para uma nova inscrição com novo user
    """
    person = subscription.person

    local = '{}'.format(
        event.place,
    )

    event_url = absoluteuri.reverse(
        'public:hotsite',
        kwargs={
            'slug': event.slug,
        }
    )

    # @TODO set event.date_start to period
    body = render_to_string('mailer/notify_user_and_subscription.html', {
        'event': event,
        'event_url': event_url,
        # 'gender_article': 'a' if person.gender == 'F' else 'o',
        'gender_article': 'o(a)',
        'person': person,
        'period': event.date_start,
        'count': subscription.count,
        'complete_sign_up_link': link,
        'date': subscription.created,
        'local': local
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
