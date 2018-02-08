import absoluteuri
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from gatheros_event.models import Event
from mailer.tasks import send_mail


@receiver(post_save, sender=Event)
def send_email_on_new_event(instance, raw, created, **_):

    if raw is True or not instance or not created:
        return

    link = absoluteuri.reverse(
        'public:hotsite',
        kwargs={
            'slug': instance.slug,
        }
    )

    body = """
    
        Novo evento: {0}
         
            Criado por: {1}
            
            Link: {2}
            
    """.format(instance.name, instance.organization.name, link)

    send_mail(body=body, subject="Novo evento!", to=settings.SALES_ALERT_EMAILS)
