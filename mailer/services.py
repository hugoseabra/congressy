""" Mailer service. """
import absoluteuri
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.models import User
from gatheros_subscription.helpers.voucher import (
    create_voucher,
    get_voucher_file_name,
)
from mailer import exception, checks

CELERY = False

if settings.DEBUG:
    from .tasks import MailerAttachment, send_mail
else:
    try:
        from .worker import MailerAttachment, send_mail

        CELERY = True
    except ImportError:
        from .tasks import MailerAttachment, send_mail


# =========================== SUBSCRIBER EMAILS ============================= #
def notify_new_unpaid_subscription_boleto(event, transaction):
    """
    Notifica participante de nova inscrição de um lote não-pago pelo método de
    boleto.
    """
    subscription = transaction.subscription
    person = subscription.person

    checks.check_notification_transaction_unpaid_boleto(transaction)

    boleto_url = transaction.boleto_url

    event_url = absoluteuri.reverse(
        'public:hotsite',
        kwargs={
            'slug': event.slug,
        }
    )

    # @TODO set event.date_start to period
    template_name = 'mailer/subscription/notify_unpaid_subscription.html'
    body = render_to_string(template_name, {
        'person': person,
        'event': event,
        'period': event.date_start,
        'event_url': event_url,
        'date': subscription.created,
        'has_voucher': False,
        'boleto_url': boleto_url,
        'my_account_url': absoluteuri.reverse('front:start'),
        'reset_password_url': absoluteuri.reverse('public:password_reset'),
        'password_set_url': None,

    })

    sender = send_mail.delay if CELERY else send_mail

    return sender(
        subject='Inscrição: {}'.format(event.name),
        body=body,
        to=person.email,
        reply_to=event.organization.email,
    )


def notify_paid_subscription_boleto(event, transaction):
    """
    Notifica participante de nova inscrição de um lote pago pelo método de
    boleto.
    """
    subscription = transaction.subscription
    person = subscription.person

    checks.check_notification_transaction_paid_boleto(transaction)

    # Se inscrição confirmada, envia o voucher.
    voucher_attach = MailerAttachment(
        name=get_voucher_file_name(subscription),
        content=create_voucher(subscription),
        mime='application/pdf'
    )

    event_url = absoluteuri.reverse(
        'public:hotsite',
        kwargs={
            'slug': event.slug,
        }
    )

    # @TODO set event.date_start to period
    template_name = 'mailer/subscription/notify_paid_subscription.html'
    body = render_to_string(template_name, {
        'person': person,
        'event': event,
        'period': event.date_start,
        'event_url': event_url,
        'date': subscription.created,
        'has_voucher': True,
        'boleto_url': None,
        'my_account_url': absoluteuri.reverse('front:start'),
        'reset_password_url': absoluteuri.reverse('public:password_reset'),
        'password_set_url': None,
    })

    sender = send_mail.delay if CELERY else send_mail

    return sender(
        subject='Inscrição: {}'.format(event.name),
        body=body,
        to=person.email,
        reply_to=event.organization.email,
        attachment=voucher_attach,
    )


def notify_new_user_and_unpaid_subscription_boleto(event, transaction):
    subscription = transaction.subscription
    person = subscription.person

    checks.check_notification_transaction_unpaid_boleto(transaction)

    boleto_url = transaction.boleto_url

    event_url = absoluteuri.reverse(
        'public:hotsite',
        kwargs={
            'slug': event.slug,
        }
    )

    user = person.user

    if isinstance(user, User):
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        password_set_url = absoluteuri.reverse(
            'password_reset_confirm',
            kwargs={
                'uidb64': uid,
                'token': token,
            }
        )

        # @TODO set event.date_start to period
        template_name = \
            'mailer/subscription/notify_new_user_and_unpaid_subscription.html'

        body = render_to_string(template_name, {
            'person': person,
            'event': event,
            'period': event.date_start,
            'event_url': event_url,
            'date': subscription.created,
            'has_voucher': False,
            'boleto_url': boleto_url,
            'my_account_url': absoluteuri.reverse('front:start'),
            'reset_password_url': absoluteuri.reverse('public:password_reset'),
            'password_set_url': password_set_url,
        })
    else:

        # @TODO set event.date_start to period
        template_name = \
            'mailer/subscription' \
            '/notify_new_subscription_and_unpaid_subscription.html'

        body = render_to_string(template_name, {
            'person': person,
            'event': event,
            'period': event.date_start,
            'event_url': event_url,
            'date': subscription.created,
            'has_voucher': False,
            'boleto_url': boleto_url,
        })

    sender = send_mail.delay if CELERY else send_mail

    return sender(
        subject='Inscrição: {}'.format(event.name),
        body=body,
        to=person.email,
        reply_to=event.organization.email,
    )


def notify_new_user_and_paid_subscription_boleto(event, transaction):
    """
    Notifica participante de nova inscrição de um lote pago pelo método de
    cartão de crédito.
    """
    subscription = transaction.subscription

    checks.check_notification_transaction_paid_boleto(transaction)

    voucher_attach = MailerAttachment(
        name=get_voucher_file_name(subscription),
        content=create_voucher(subscription),
        mime='application/pdf'
    )

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
    password_set_url = absoluteuri.reverse(
        'password_reset_confirm',
        kwargs={
            'uidb64': uid,
            'token': token,
        }
    )

    # @TODO set event.date_start to period
    template_name = \
        'mailer/subscription/notify_new_user_and_paid_subscription.html'

    body = render_to_string(template_name, {
        'person': person,
        'event': event,
        'period': event.date_start,
        'event_url': event_url,
        'date': subscription.created,
        'has_voucher': True,
        'boleto_url': None,
        'my_account_url': absoluteuri.reverse('front:start'),
        'reset_password_url': absoluteuri.reverse('public:password_reset'),
        'password_set_url': password_set_url,
    })

    sender = send_mail.delay if CELERY else send_mail

    return sender(
        subject='Inscrição: {}'.format(event.name),
        body=body,
        to=person.email,
        reply_to=event.organization.email,
        attachment=voucher_attach,
    )


def notify_new_unpaid_subscription_credit_card(event, transaction):
    """
    Notifica participante de nova inscrição de um lote pago pelo método de
    cartão de crédito.
    """
    subscription = transaction.subscription

    checks.check_notification_transaction_unpaid_credit_card(transaction)

    person = subscription.person

    event_url = absoluteuri.reverse(
        'public:hotsite',
        kwargs={
            'slug': event.slug,
        }
    )

    # @TODO set event.date_start to period
    template_name = 'mailer/subscription/notify_unpaid_subscription.html'
    body = render_to_string(template_name, {
        'person': person,
        'event': event,
        'period': event.date_start,
        'event_url': event_url,
        'date': subscription.created,
        'has_voucher': False,
        'boleto_url': None,
        'my_account_url': absoluteuri.reverse('front:start'),
        'reset_password_url': absoluteuri.reverse('public:password_reset'),
    })

    sender = send_mail.delay if CELERY else send_mail

    return sender(
        subject='Inscrição: {}'.format(event.name),
        body=body,
        to=person.email,
        reply_to=event.organization.email,
    )


def notify_new_refused_subscription_credit_card(event, transaction):
    """
    Notifica participante de nova inscrição de um lote pago pelo método de
    cartão de crédito e o cartão foi recusado.
    """
    subscription = transaction.subscription

    checks.check_notification_transaction_refused_credit_card(transaction)

    person = subscription.person

    event_url = absoluteuri.reverse(
        'public:hotsite',
        kwargs={
            'slug': event.slug,
        }
    )

    # @TODO set event.date_start to period
    template_name = 'mailer/subscription/notify_refused_subscription.html'
    body = render_to_string(template_name, {
        'person': person,
        'event': event,
        'period': event.date_start,
        'event_url': event_url,
        'date': subscription.created,
        'has_voucher': False,
        'boleto_url': None,
        'my_account_url': absoluteuri.reverse('front:start'),
        'reset_password_url': absoluteuri.reverse('public:password_reset'),
    })

    sender = send_mail.delay if CELERY else send_mail

    return sender(
        subject='Inscrição: {} - pagamento recusado'.format(event.name),
        body=body,
        to=person.email,
        reply_to=event.organization.email,
    )


def notify_new_refused_subscription_boleto(event, transaction):
    """
    Notifica participante de nova inscrição de um lote pago pelo método de
    cartão de crédito e o cartão foi recusado.
    """
    subscription = transaction.subscription

    checks.check_notification_transaction_refused_boleto(transaction)

    person = subscription.person

    event_url = absoluteuri.reverse(
        'public:hotsite',
        kwargs={
            'slug': event.slug,
        }
    )

    # @TODO set event.date_start to period
    template_name = 'mailer/subscription/notify_refused_subscription.html'
    body = render_to_string(template_name, {
        'person': person,
        'event': event,
        'period': event.date_start,
        'event_url': event_url,
        'date': subscription.created,
        'has_voucher': False,
        'boleto_url': None,
        'my_account_url': absoluteuri.reverse('front:start'),
        'reset_password_url': absoluteuri.reverse('public:password_reset'),
    })

    sender = send_mail.delay if CELERY else send_mail

    return sender(
        subject='Inscrição: {} - pagamento recusado'.format(event.name),
        body=body,
        to=person.email,
        reply_to=event.organization.email,
    )


def notify_new_paid_subscription_credit_card(event, transaction):
    """
    Notifica participante de nova inscrição de um lote pago pelo método de
    cartão de crédito.
    """
    subscription = transaction.subscription

    checks.check_notification_transaction_paid_credit_card(transaction)

    voucher_attach = MailerAttachment(
        name=get_voucher_file_name(subscription),
        content=create_voucher(subscription),
        mime='application/pdf'
    )

    person = subscription.person

    event_url = absoluteuri.reverse(
        'public:hotsite',
        kwargs={
            'slug': event.slug,
        }
    )

    # @TODO set event.date_start to period
    template_name = 'mailer/subscription/notify_paid_subscription.html'
    body = render_to_string(template_name, {
        'person': person,
        'event': event,
        'period': event.date_start,
        'event_url': event_url,
        'date': subscription.created,
        'has_voucher': True,
        'boleto_url': None,
        'my_account_url': absoluteuri.reverse('front:start'),
        'reset_password_url': absoluteuri.reverse('public:password_reset'),
    })

    sender = send_mail.delay if CELERY else send_mail

    return sender(
        subject='Inscrição: {}'.format(event.name),
        body=body,
        to=person.email,
        reply_to=event.organization.email,
        attachment=voucher_attach,
    )


def notify_new_user_and_unpaid_subscription_credit_card(event, transaction):
    """
    Notifica participante de nova inscrição de um lote pago pelo método de
    cartão de crédito.
    """
    subscription = transaction.subscription

    checks.check_notification_transaction_unpaid_credit_card(transaction)

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
    password_set_url = absoluteuri.reverse(
        'password_reset_confirm',
        kwargs={
            'uidb64': uid,
            'token': token,
        }
    )

    # @TODO set event.date_start to period
    template_name = \
        'mailer/subscription/notify_new_user_and_unpaid_subscription.html'

    body = render_to_string(template_name, {
        'person': person,
        'event': event,
        'period': event.date_start,
        'event_url': event_url,
        'date': subscription.created,
        'has_voucher': False,
        'boleto_url': None,
        'my_account_url': absoluteuri.reverse('front:start'),
        'reset_password_url': absoluteuri.reverse('public:password_reset'),
        'password_set_url': password_set_url,
    })

    sender = send_mail.delay if CELERY else send_mail

    return sender(
        subject='Inscrição: {}'.format(event.name),
        body=body,
        to=person.email,
        reply_to=event.organization.email,
    )


def notify_new_user_and_refused_subscription_credit_card(event, transaction):
    """
    Notifica participante de nova inscrição de um lote pago pelo método de
    cartão de crédito.
    """
    subscription = transaction.subscription

    checks.check_notification_transaction_refused_credit_card(transaction)

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
    password_set_url = absoluteuri.reverse(
        'password_reset_confirm',
        kwargs={
            'uidb64': uid,
            'token': token,
        }
    )

    # @TODO set event.date_start to period
    template_name = \
        'mailer/subscription/notify_new_user_and_refused_subscription.html'

    body = render_to_string(template_name, {
        'person': person,
        'event': event,
        'period': event.date_start,
        'event_url': event_url,
        'date': subscription.created,
        'has_voucher': False,
        'boleto_url': None,
        'my_account_url': absoluteuri.reverse('front:start'),
        'reset_password_url': absoluteuri.reverse('public:password_reset'),
        'password_set_url': password_set_url,
    })

    sender = send_mail.delay if CELERY else send_mail

    return sender(
        subject='Inscrição: {} - pagamento recusado'.format(event.name),
        body=body,
        to=person.email,
        reply_to=event.organization.email,
    )


def notify_new_user_and_refused_subscription_boleto(event, transaction):
    """
    Notifica participante de nova inscrição de um lote pago pelo método de
    boleto, possivelmente por uma falha qualquer.
    """
    subscription = transaction.subscription

    checks.check_notification_transaction_refused_boleto(transaction)

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
    password_set_url = absoluteuri.reverse(
        'password_reset_confirm',
        kwargs={
            'uidb64': uid,
            'token': token,
        }
    )

    # @TODO set event.date_start to period
    template_name = \
        'mailer/subscription/notify_new_user_and_refused_subscription.html'

    body = render_to_string(template_name, {
        'person': person,
        'event': event,
        'period': event.date_start,
        'event_url': event_url,
        'date': subscription.created,
        'has_voucher': False,
        'boleto_url': None,
        'my_account_url': absoluteuri.reverse('front:start'),
        'reset_password_url': absoluteuri.reverse('public:password_reset'),
        'password_set_url': password_set_url,
    })

    sender = send_mail.delay if CELERY else send_mail

    return sender(
        subject='Inscrição: {} - pagamento recusado'.format(event.name),
        body=body,
        to=person.email,
        reply_to=event.organization.email,
    )


def notify_new_user_and_paid_subscription_credit_card(event, transaction):
    """
    Notifica participante de nova inscrição de um lote pago pelo método de
    cartão de crédito.
    """
    subscription = transaction.subscription

    checks.check_notification_transaction_paid_credit_card(transaction)

    voucher_attach = MailerAttachment(
        name=get_voucher_file_name(subscription),
        content=create_voucher(subscription),
        mime='application/pdf'
    )

    person = subscription.person

    event_url = absoluteuri.reverse(
        'public:hotsite',
        kwargs={
            'slug': event.slug,
        }
    )

    # @TODO set event.date_start to period
    template_name = \
        'mailer/subscription/notify_new_user_and_paid_subscription.html'

    body = render_to_string(template_name, {
        'person': person,
        'event': event,
        'period': event.date_start,
        'event_url': event_url,
        'date': subscription.created,
        'has_voucher': True,
        'boleto_url': None,
        'my_account_url': absoluteuri.reverse('front:start'),
        'reset_password_url': absoluteuri.reverse('public:password_reset'),
        'password_set_url': '',
    })

    sender = send_mail.delay if CELERY else send_mail

    return sender(
        subject='Inscrição: {}'.format(event.name),
        body=body,
        to=person.email,
        reply_to=event.organization.email,
        attachment=voucher_attach,
    )


def notify_new_free_subscription(event, subscription):
    """
    Notifica participante de nova inscrição de um lote gratuito.
    """
    if not subscription.free:
        raise exception.NotifcationError(
            'Lote de inscrição não é gratuito. A notificação para inscrição'
            ' gratuita não pode ser realizada.'
        )

    if subscription.status != subscription.CONFIRMED_STATUS:
        raise exception.NotifcationError(
            "Notificação de inscrição gratuita deve sempre estar confirmada."
            " A notificação não será realizada porque a inscrição ainda não"
            " está como confirmada.."
        )

    # Se inscrição confirmada, envia o voucher.
    voucher_attach = MailerAttachment(
        name=get_voucher_file_name(subscription),
        content=create_voucher(subscription),
        mime='application/pdf'
    )

    person = subscription.person

    event_url = absoluteuri.reverse(
        'public:hotsite',
        kwargs={
            'slug': event.slug,
        }
    )

    # @TODO set event.date_start to
    template_name = 'mailer/subscription/notify_free_subscription.html'
    body = render_to_string(template_name, {
        'person': person,
        'event': event,
        'period': event.date_start,
        'event_url': event_url,
        'date': subscription.created,
        'has_voucher': True,
        'my_account_url': absoluteuri.reverse('front:start'),
        'reset_password_url': absoluteuri.reverse('public:password_reset'),
    })

    sender = send_mail.delay if CELERY else send_mail

    return sender(
        subject='Inscrição: {}'.format(event.name),
        body=body,
        to=person.email,
        reply_to=event.organization.email,
        attachment=voucher_attach,
    )


def notify_new_user_and_free_subscription(event, subscription):
    """
    Notifica participante de nova conta e nova inscrição de um lote gratuito.
    """
    if not subscription.free:
        raise exception.NotifcationError(
            'Lote de inscrição não é gratuito. A notificação para inscrição'
            ' gratuita não pode ser realizada.'
        )

    if subscription.status != subscription.CONFIRMED_STATUS:
        raise exception.NotifcationError(
            "Notificação de inscrição gratuita deve sempre estar confirmada."
            " A notificação não será realizada porque a inscrição ainda não"
            " está como confirmada.."
        )

    # Se inscrição confirmada, envia o voucher.
    voucher_attach = MailerAttachment(
        name=get_voucher_file_name(subscription),
        content=create_voucher(subscription),
        mime='application/pdf'
    )

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
    password_set_url = absoluteuri.reverse(
        'password_reset_confirm',
        kwargs={
            'uidb64': uid,
            'token': token,
        }
    )

    # @TODO set event.date_start to period
    template_name = \
        'mailer/subscription/notify_new_user_and_free_subscription.html'

    body = render_to_string(template_name, {
        'person': person,
        'event': event,
        'period': event.date_start,
        'event_url': event_url,
        'date': subscription.created,
        'has_voucher': True,
        'password_set_url': password_set_url,
    })

    sender = send_mail.delay if CELERY else send_mail

    return sender(
        subject='Inscrição: {}'.format(event.name),
        body=body,
        to=person.email,
        reply_to=event.organization.email,
        attachment=voucher_attach,
    )


def notify_refunded_subscription_boleto(event, transaction):
    """
    Notifica participante de reembolso de um lote pago pelo método de
    boleto.
    """
    subscription = transaction.subscription

    checks.check_notification_transaction_refunded_boleto(transaction)

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
    password_set_url = absoluteuri.reverse(
        'password_reset_confirm',
        kwargs={
            'uidb64': uid,
            'token': token,
        }
    )

    # @TODO set event.date_start to period
    template_name = \
        'mailer/subscription/notify_refunded_subscription.html'

    body = render_to_string(template_name, {
        'person': person,
        'event': event,
        'period': event.date_start,
        'event_url': event_url,
        'date': subscription.created,
        'has_voucher': False,
        'boleto_url': None,
        'my_account_url': absoluteuri.reverse('front:start'),
        'reset_password_url': absoluteuri.reverse('public:password_reset'),
        'password_set_url': password_set_url,
    })

    sender = send_mail.delay if CELERY else send_mail

    return sender(
        subject='Reembolso de Inscrição: {}'.format(event.name),
        body=body,
        to=person.email,
        reply_to=event.organization.email,
    )


def notify_refunded_subscription_credit_card(event, transaction):
    """
    Notifica participante de reembolso de um lote pago pelo método de
    cartão de crédito.
    """
    subscription = transaction.subscription

    checks.check_notification_transaction_refunded_credit_card(transaction)

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
    password_set_url = absoluteuri.reverse(
        'password_reset_confirm',
        kwargs={
            'uidb64': uid,
            'token': token,
        }
    )

    # @TODO set event.date_start to period
    template_name = \
        'mailer/subscription/notify_refunded_subscription.html'

    body = render_to_string(template_name, {
        'person': person,
        'event': event,
        'period': event.date_start,
        'event_url': event_url,
        'date': subscription.created,
        'has_voucher': False,
        'boleto_url': None,
        'my_account_url': absoluteuri.reverse('front:start'),
        'reset_password_url': absoluteuri.reverse('public:password_reset'),
        'password_set_url': password_set_url,
    })

    sender = send_mail.delay if CELERY else send_mail

    return sender(
        subject='Reembolso de Inscrição: {}'.format(event.name),
        body=body,
        to=person.email,
        reply_to=event.organization.email,
    )


def notify_chargedback_subscription(event, transaction):
    """
    Notifica participante de reembolso de um lote pago pelo método de
    boleto.
    """
    subscription = transaction.subscription

    person = subscription.person

    event_url = absoluteuri.reverse('public:hotsite', kwargs={
        'slug': event.slug,
    })

    # @TODO set event.date_start to period
    template_name = \
        'mailer/subscription/notify_chargedback_subscription.html'

    body = render_to_string(template_name, {
        'person': person,
        'event': event,
        'period': event.date_start,
        'event_url': event_url,
        'date': subscription.created,
        'has_voucher': False,
        'boleto_url': None,
        'my_account_url': absoluteuri.reverse('front:start'),
        'reset_password_url': absoluteuri.reverse('public:password_reset'),
    })

    sender = send_mail.delay if CELERY else send_mail

    return sender(
        subject='Chargedback de Inscrição: {}'.format(event.name),
        body=body,
        to=person.email,
        reply_to=event.organization.email,
    )


# ============================ ACCOUNT EMAILS =============================== #
def notify_new_user(context):
    """
    Define a notificação para um usuario na plataforma.
    """

    body = render_to_string('mailer/account_confirmation_email.html',
                            context=context)

    subject = 'Confirmação de cadastro na {0}'.format(context['site_name'])

    sender = send_mail.delay if CELERY else send_mail

    return sender(
        subject=subject,
        body=body,
        to=context['email'],
    )


def notify_new_partner(context):
    """
    Define a notificação para um novo parceiro na plataforma.
    """

    body = render_to_string(
        'mailer/notify_partner_registration_email.html',
        context=context
    )

    subject = 'Cadastro de parceria na  {0}'.format(context['site_name'])

    sender = send_mail.delay if CELERY else send_mail

    return sender(
        subject=subject,
        body=body,
        to=context['partner_email'],
    )


def notify_reset_password(context):
    """
    Define a notificação para um usuario na plataforma.
    """

    body = render_to_string('mailer/password_reset_email.html',
                            context=context)

    subject = 'Redefina sua senha na {0}'.format(context['site_name'])

    sender = send_mail.delay if CELERY else send_mail

    return sender(
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

    sender = send_mail.delay if CELERY else send_mail

    return sender(
        subject=subject,
        body=body,
        to=context['email'],
    )


# ============================ PARTNER EMAILS =============================== #

def notify_partner_contract(context):
    """
    Define a notificação para um parceiro quando o mesmo é vinculado a um
    evento.
    """

    subject = 'Parceria Congressy: Vinculado ao evento {0}'.format(context[
                                                                       'event'])

    body = render_to_string('mailer/notify_partner_contract_email.html',
                            context=context)

    sender = send_mail.delay if CELERY else send_mail

    return sender(
        subject=subject,
        body=body,
        to=context['partner_email'],
    )


# ============================ INTERNAL EMAILS ============================== #
def notify_new_partner_internal(context):
    """
    Define a notificação interna para o comercial no evento de cadastro um novo
    parceiro na plataforma.
    """

    body = render_to_string(
        'mailer/notify_partner_registration_internal_email.html',
        context=context)

    subject = 'Novo parceiro cadastrado: {0}'.format(context['partner_name'])

    sender = send_mail.delay if CELERY else send_mail

    return sender(
        subject=subject,
        body=body,
        to=settings.SALES_ALERT_EMAILS,
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

    sender = send_mail.delay if CELERY else send_mail

    sender(
        body=body,
        subject="Novo evento: {}".format(event.name),
        to=settings.SALES_ALERT_EMAILS
    )


# ======================= MANAGE ORGANIZER EMAILS =========================== #
def notify_open_boleto(transaction):
    """
    Notifica participante sobre novo boleto disponível para pagamento.
    """
    subscription = transaction.subscription
    event = subscription.event
    person = subscription.person

    checks.check_notification_transaction_unpaid_boleto(transaction)

    boleto_url = transaction.boleto_url

    event_url = absoluteuri.reverse(
        'public:hotsite',
        kwargs={
            'slug': event.slug,
        }
    )

    user = person.user
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    password_set_url = absoluteuri.reverse(
        'password_reset_confirm',
        kwargs={
            'uidb64': uid,
            'token': token,
        }
    )

    # @TODO set event.date_start to period
    template_name = \
        'mailer/subscription/notify_unpaid_boleto.html'

    body = render_to_string(template_name, {
        'person': person,
        'event': event,
        'period': event.date_start,
        'event_url': event_url,
        'date': subscription.created,
        'has_voucher': False,
        'boleto_url': boleto_url,
        'my_account_url': absoluteuri.reverse('front:start'),
        'reset_password_url': absoluteuri.reverse('public:password_reset'),
        'password_set_url': password_set_url,
    })

    sender = send_mail.delay if CELERY else send_mail

    return sender(
        subject='Boleto disponível: {}'.format(event.name),
        body=body,
        to=person.email,
        reply_to=event.organization.email,
    )


# =========================== ORGANIZATION  EMAILS ========================== #
def notify_invite(organization, link, inviter, invited_person, email):
    """
        Define a notificação para um novo convite
    """

    body = render_to_string('mailer/notify_invitation.html', {
        'organizacao': organization.name,
        'hospedeiro': inviter,
        'convidado': invited_person,
        'link': link,
    })

    sender = send_mail.delay if CELERY else send_mail

    return sender(
        subject='Convite: {}'.format(organization.name),
        body=body,
        to=email,
        reply_to=organization.email,
    )
