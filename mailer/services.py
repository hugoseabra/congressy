""" Mailer service. """
import os
import time
from datetime import timedelta, datetime

import absoluteuri
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from gatheros_event.models import Member
from gatheros_subscription.helpers.voucher import create_voucher
from mailer import exception, checks
from .worker import send_mail


# =============================== HELPERS =================================== #
def send(event, body, to, subject, attachment_file_path=None):
    """ Dados necessários para envio do e-mail. """
    org = event.organization

    if org.email:
        author_email = org.email
    else:
        members = org.members.filter(
            group=Member.ADMIN,
            person__user__is_superuser=False,
        ).order_by('created')

        if members.count() == 0:
            members = org.members.filter(
                group=Member.ADMIN,
            ).order_by('created')

        member = members.first()
        author_email = member.person.email

    kwargs = {
        'subject': subject,
        'body': body,
        'to': to,
        'reply_to': author_email,
    }

    if attachment_file_path:
        kwargs.update({
            'attachment_file_path': attachment_file_path,
        })

    # Vamos processar dando tempo para o arquivo propagar em todos os
    # servidores
    sender = send_mail.apply_async
    return sender(
        kwargs=kwargs,
        eta=datetime.now() + timedelta(seconds=30),  # exec after 30 secs
    )


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

    return send(
        event=event,
        body=body,
        to=person.email,
        subject='Inscrição: {}'.format(event.name)
    )


def notify_paid_subscription_boleto(event, transaction):
    """
    Notifica participante de nova inscrição de um lote pago pelo método de
    boleto.
    """
    subscription = transaction.subscription
    person = subscription.person

    checks.check_notification_transaction_paid_boleto(transaction)

    # Precisamos de outros serviços para gerar qrcode, barcode e PDF.from
    # Vamos saber se esses serviços possuem delay e/ou estão disponíveis. Caso
    # não, vamos levantar uma exceção.
    voucher_file = ''
    counter = 1
    while os.path.isfile(voucher_file) is False:
        if counter == 50:  # 50 tentativas
            raise Exception('Não foi possível criar arquivo de voucher.')

        elif counter > 1:
            time.sleep(secs=5)

        voucher_file = create_voucher(subscription, save=True)
        counter += 1

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

    return send(event=event,
                body=body,
                to=person.email,
                subject='Inscrição: {}'.format(event.name),
                attachment_file_path=voucher_file)


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

    return send(
        event=event,
        body=body,
        to=person.email,
        subject='Inscrição: {}'.format(event.name)
    )


def notify_new_user_and_paid_subscription_boleto(event, transaction):
    """
    Notifica participante de nova inscrição de um lote pago pelo método de
    boleto.
    """
    subscription = transaction.subscription

    checks.check_notification_transaction_paid_boleto(transaction)

    # Precisamos de outros serviços para gerar qrcode, barcode e PDF.from
    # Vamos saber se esses serviços possuem delay e/ou estão disponíveis. Caso
    # não, vamos levantar uma exceção.
    voucher_file = ''
    counter = 1
    while os.path.isfile(voucher_file) is False:
        if counter == 50:  # 50 tentativas
            raise Exception('Não foi possível criar arquivo de voucher.')

        elif counter > 1:
            time.sleep(secs=5)

        voucher_file = create_voucher(subscription, save=True)
        counter += 1

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
        'boleto_url': transaction.boleto_url,
        'my_account_url': absoluteuri.reverse('front:start'),
        'reset_password_url': absoluteuri.reverse('public:password_reset'),
        'password_set_url': password_set_url,
    })

    return send(
        event=event,
        body=body,
        to=person.email,
        subject='Inscrição: {}'.format(event.name),
        attachment_file_path=voucher_file,
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

    return send(
        event=event,
        body=body,
        to=person.email,
        subject='Inscrição: {}'.format(event.name)
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

    return send(
        event=event,
        body=body,
        to=person.email,
        subject='Inscrição: {} - pagamento recusado'.format(event.name),
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

    return send(
        event=event,
        body=body,
        to=person.email,
        subject='Inscrição: {} - pagamento recusado'.format(event.name),
    )


def notify_new_paid_subscription_credit_card(event, transaction):
    """
    Notifica participante de nova inscrição de um lote pago pelo método de
    cartão de crédito.
    """
    subscription = transaction.subscription

    checks.check_notification_transaction_paid_credit_card(transaction)

    # Precisamos de outros serviços para gerar qrcode, barcode e PDF.from
    # Vamos saber se esses serviços possuem delay e/ou estão disponíveis. Caso
    # não, vamos levantar uma exceção.
    voucher_file = ''
    counter = 1
    while os.path.isfile(voucher_file) is False:
        if counter == 50:  # 50 tentativas
            raise Exception('Não foi possível criar arquivo de voucher.')

        elif counter > 1:
            time.sleep(secs=5)

        voucher_file = create_voucher(subscription, save=True)
        counter += 1

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

    return send(
        event=event,
        body=body,
        to=person.email,
        subject='Inscrição: {}'.format(event.name),
        attachment_file_path=voucher_file,
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

    return send(
        event=event,
        subject='Inscrição: {}'.format(event.name),
        body=body,
        to=person.email,
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

    return send(
        event=event,
        subject='Inscrição: {} - pagamento recusado'.format(event.name),
        body=body,
        to=person.email,
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

    return send(
        event=event,
        body=body,
        to=person.email,
        subject='Inscrição: {} - pagamento recusado'.format(event.name),
    )


def notify_new_user_and_paid_subscription_credit_card(event, transaction):
    """
    Notifica participante de nova inscrição de um lote pago pelo método de
    cartão de crédito.
    """
    subscription = transaction.subscription

    checks.check_notification_transaction_paid_credit_card(transaction)

    # Precisamos de outros serviços para gerar qrcode, barcode e PDF.from
    # Vamos saber se esses serviços possuem delay e/ou estão disponíveis. Caso
    # não, vamos levantar uma exceção.
    voucher_file = ''
    counter = 1
    while os.path.isfile(voucher_file) is False:
        if counter == 50:  # 50 tentativas
            raise Exception('Não foi possível criar arquivo de voucher.')

        elif counter > 1:
            time.sleep(secs=5)

        voucher_file = create_voucher(subscription, save=True)
        counter += 1

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

    return send(
        event=event,
        body=body,
        to=person.email,
        subject='Inscrição: {}'.format(event.name),
        attachment_file_path=voucher_file,
    )


def notify_new_user_and_paid_subscription_credit_card_with_discrepancy(event,
                                                                       transaction):
    """
    Notifica participante de nova inscrição de um lote pago pelo método de
    cartão de crédito.
    """
    subscription = transaction.subscription

    checks.check_notification_transaction_paid_credit_card(transaction)

    # Precisamos de outros serviços para gerar qrcode, barcode e PDF.from
    # Vamos saber se esses serviços possuem delay e/ou estão disponíveis. Caso
    # não, vamos levantar uma exceção.
    voucher_file = ''
    counter = 1
    while os.path.isfile(voucher_file) is False:
        if counter == 50:  # 50 tentativas
            raise Exception('Não foi possível criar arquivo de voucher.')

        elif counter > 1:
            time.sleep(secs=5)

        voucher_file = create_voucher(subscription, save=True)
        counter += 1

    person = subscription.person

    event_url = absoluteuri.reverse(
        'public:hotsite',
        kwargs={
            'slug': event.slug,
        }
    )
    template_name = \
        'mailer/subscription/notify_new_user_and_paid_subscription_credit' \
        '_card_with_discrepancy.html'

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

    return send(
        event=event,
        body=body,
        to=person.email,
        subject='Inscrição: {}'.format(event.name),
        attachment_file_path=voucher_file,
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

    # Precisamos de outros serviços para gerar qrcode, barcode e PDF.from
    # Vamos saber se esses serviços possuem delay e/ou estão disponíveis. Caso
    # não, vamos levantar uma exceção.
    voucher_file = ''
    counter = 1
    while os.path.isfile(voucher_file) is False:
        if counter == 50:  # 50 tentativas
            raise Exception('Não foi possível criar arquivo de voucher.')

        elif counter > 1:
            time.sleep(secs=5)

        voucher_file = create_voucher(subscription, save=True)
        counter += 1

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

    return send(
        event=event,
        body=body,
        to=person.email,
        subject='Inscrição: {}'.format(event.name),
        attachment_file_path=voucher_file,
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

    # Precisamos de outros serviços para gerar qrcode, barcode e PDF.from
    # Vamos saber se esses serviços possuem delay e/ou estão disponíveis. Caso
    # não, vamos levantar uma exceção.
    voucher_file = ''
    counter = 1
    while os.path.isfile(voucher_file) is False:
        if counter == 50:  # 50 tentativas
            raise Exception('Não foi possível criar arquivo de voucher.')

        elif counter > 1:
            time.sleep(secs=5)

        voucher_file = create_voucher(subscription, save=True)
        counter += 1

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

    return send(
        event=event,
        body=body,
        to=person.email,
        subject='Inscrição: {}'.format(event.name),
        attachment_file_path=voucher_file,
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

    return send(
        event=event,
        body=body,
        to=person.email,
        subject='Reembolso de Inscrição: {}'.format(event.name),
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

    return send(
        event=event,
        body=body,
        to=person.email,
        subject='Reembolso de Inscrição: {}'.format(event.name),
    )


def notify_pending_refund_subscription(event, transaction):
    """
    Notifica participante quando notificação possui pendência de reembolso.
    """
    subscription = transaction.subscription

    checks.check_notification_transaction_pending_refund_boleto(transaction)

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
        'mailer/subscription/notify_pending_refund_subscription.html'

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

    return send(
        event=event,
        body=body,
        to=person.email,
        subject='Reembolso de Inscrição em'
                ' Andamento: {}'.format(event.name),
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

    return send(
        event=event,
        body=body,
        to=person.email,
        subject='Chargedback de Inscrição: {}'.format(event.name),
    )


def notify_paid_with_incoming_installment(event, transaction):
    """
    Notifica participante de inscrição existente pagamento de parcela
    """
    subscription = transaction.subscription
    person = subscription.person

    event_url = absoluteuri.reverse(
        'public:hotsite',
        kwargs={
            'slug': event.slug,
        }
    )

    template_name = \
        'mailer/subscription/notify_paid_with_incoming_installment.html'
    body = render_to_string(template_name, {
        'person': person,
        'event': event,
        'is_new': subscription.notified is False,
        'part': transaction.installment_part,
        'period': event.date_start,
        'event_url': event_url,
        'date': subscription.created,
        'has_voucher': False,
        'boleto_url': None,
        'my_account_url': absoluteuri.reverse('front:start'),
        'reset_password_url': absoluteuri.reverse('public:password_reset'),
        'password_set_url': None,
    })

    return send(
        event=event,
        body=body,
        to=person.email,
        subject='Inscrição: {}'.format(event.name),
    )


def notify_unpaid_installment(event, transaction):
    """
    Notifica participante de inscrição existente pagamento de parcela
    """
    subscription = transaction.subscription
    person = subscription.person

    event_url = absoluteuri.reverse(
        'public:hotsite',
        kwargs={
            'slug': event.slug,
        }
    )

    template_name = 'mailer/subscription/notify_unpaid_installment.html'
    body = render_to_string(template_name, {
        'person': person,
        'event': event,
        'is_new': subscription.notified is False,
        'part': transaction.installment_part,
        'period': event.date_start,
        'event_url': event_url,
        'date': subscription.created,
        'has_voucher': False,
        'boleto_url': transaction.boleto_url,
        'my_account_url': absoluteuri.reverse('front:start'),
        'reset_password_url': absoluteuri.reverse('public:password_reset'),
        'password_set_url': None,
    })

    return send(
        event=event,
        body=body,
        to=person.email,
        subject='Inscrição: {}'.format(event.name),
    )


def notify_installment_with_discrepancy(event, transaction):
    """
    Notifica participante de inscrição existente pagamento de parcela e uma
    discrepância nos valores, ele deve consultar o organizador
    """
    subscription = transaction.subscription
    person = subscription.person

    event_url = absoluteuri.reverse(
        'public:hotsite',
        kwargs={
            'slug': event.slug,
        }
    )

    org = event.organization
    author_phone = None

    if org.email:
        author_email = org.email
    else:
        member = event.organization.members.first()
        author_email = member.person.email

    if org.phone:
        author_phone = org.phone

    template_name = \
        'mailer/subscription/notify_paid_installment_discrepancy.html'
    body = render_to_string(template_name, {
        'person': person,
        'organizer_email': author_email,
        'organizer_phone': author_phone,
        'event': event,
        'is_new': subscription.notified is False,
        'part': transaction.installment_part,
        'period': event.date_start,
        'event_url': event_url,
        'date': subscription.created,
        'has_voucher': False,
        'boleto_url': None,
        'my_account_url': absoluteuri.reverse('front:start'),
        'reset_password_url': absoluteuri.reverse('public:password_reset'),
        'password_set_url': None,
    })

    return send(
        event=event,
        body=body,
        to=person.email,
        subject='Inscrição: {}'.format(event.name),
    )


# ============================ ACCOUNT EMAILS =============================== #
def notify_new_user(context):
    """
    Define a notificação para um usuario na plataforma.
    """

    body = render_to_string('mailer/account_confirmation_email.html',
                            context=context)

    subject = 'Confirmação de cadastro na {0}'.format(context['site_name'])

    sender = send_mail.apply_async

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

    sender = send_mail.apply_async

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

    sender = send_mail.apply_async

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

    sender = send_mail.apply_async

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

    sender = send_mail.apply_async

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

    sender = send_mail.apply_async

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

    org = event.organization
    if org.email:
        author_email = org.email
    else:
        member = event.organization.members.first()
        author_email = member.person.email

    body = render_to_string(
        template_name='mailer/notify_new_event.html',
        context={
            'event': event,
            'author_email': author_email,
            'link': link
        }
    )

    sender = send_mail.apply_async

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

    return send(
        event=event,
        body=body,
        to=person.email,
        subject='Boleto disponível: {}'.format(event.name),
    )


# =========================== ORGANIZATION  EMAILS ========================== #
def notify_invite(organization, link, inviter, invited_person, email):
    """
        Define a notificação para um novo convite
    """

    members = organization.members.filter(
        group=Member.ADMIN,
        person__user__is_superuser=False,
    ).order_by('created')

    if members.count() == 0:
        members = organization.members.filter(
            group=Member.ADMIN,
        ).order_by('created')

    member = members.first()

    if organization.email:
        org_admin_email = organization.email
    else:
        org_admin_email = member.person.email

    body = render_to_string('mailer/notify_invitation.html', {
        'organizacao': organization.name,
        'hospedeiro': inviter,
        'convidado': invited_person,
        'link': link,
    })

    sender = send_mail.apply_async

    return sender(
        subject='Convite: {}'.format(organization.name),
        body=body,
        to=email,
        reply_to=org_admin_email,
    )
