""" Signals do model `Organization`. """

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import six

from gatheros_event.models import Person


@receiver(post_save, sender=Person)
def update_person_related_organization(instance, raw, **_):
    """
    Atualiza nomes de Organização e Usuário assim que o nome da
    pessoa é atualizado.
    """

    # Disable when loaded by fixtures
    if raw is True:
        return

    for member in instance.members.filter(organization__internal=True):

        organization = member.organization

        for attr, value in six.iteritems(instance.get_profile_data()):
            setattr(organization, attr, value)

        organization.save()

