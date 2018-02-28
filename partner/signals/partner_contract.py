""" Signals for the `PartnerContract` model. """

from django.db.models.signals import post_save
from django.dispatch import receiver


from partner.models import PartnerContract
from mailer.services import notify_partner_contract


@receiver(post_save, sender=PartnerContract)
def notify_partner_of_contract(instance, raw, created, **_):
    """
        Sends an email to the partner em question informing that he has been
        correctly
    """

    # Disable when loaded by fixtures or not a new contract
    if raw is True or not created:
        return

    context = {
        'event': instance.event.name,
        'organizer': instance.event.organization.name,
        'partner_name': instance.partner.person.user.first_name,
        'partner_email': instance.partner.person.email,

    }

    notify_partner_contract(context=context)



