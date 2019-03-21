import json

import requests
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from attendance.models import AttendanceService, Checkin, Checkout
from gatheros_event.models import Event


@receiver(post_save, sender=Event)
def create_default_attendance(instance, raw, created, **_):
    if raw is True:
        return

    if created is True:
        AttendanceService.objects.create(
            event=instance,
            name='Credenciamento',
            with_certificate=True,
            checkout_enabled=False,
        )


@receiver(pre_save, sender=Checkin)
def trigger_checkin_pwa(instance, raw, **_):
    if raw is True:
        return

    service = instance.attendance_service

    if not service.printing_queue_webhook or not service.pwa_pin:
        return

    webhook = service.printing_queue_webhook
    if webhook.endswith('/'):
        webhook = webhook[0:len(webhook) - 1]

    r = requests.post(
        webhook,
        data=json.dumps({
            'service_id': service.pk,
            'subscription_id': str(instance.subscription_id),
            'printer_number': service.printer_number or 1,
        }),
        headers={
            'Content-Type': 'application/json',
            'PIN': service.pwa_pin,
        }
    )

    from pprint import pprint
    pprint(r)


@receiver(pre_save, sender=Checkout)
def trigger_checkout_pwa(instance, raw, **_):
    if raw is True:
        return

    checkin = instance.checkin
    service = checkin.attendance_service

    if not service.printing_queue_webhook or not service.pwa_pin:
        return

    webhook = service.printing_queue_webhook
    if webhook.endswith('/'):
        webhook = webhook[0:len(webhook) - 1]

    webhook += '/' + str(checkin.subscription_id)

    r = requests.delete(
        webhook,
        headers={
            'Content-Type': 'application/json',
            'PIN': service.pwa_pin,
        }
    )

    from pprint import pprint
    pprint(r)
