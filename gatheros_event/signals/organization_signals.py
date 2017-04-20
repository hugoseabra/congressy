from django.db.models.signals import post_save
from django.dispatch import receiver

from gatheros_event.models import Person


@receiver(post_save, sender=Person)
def update_person_related_organization(sender, instance, created, raw, **_):
    # Disable when loaded by fixtures
    if raw is True:
        return

    """
    Atualiza nomes de Organização e Usuário assim que o nome da
    pessoa é atualizado.
    """

    for member in instance.members.all():
        if not member.organization.internal:
            continue

        member.organization.name = instance.name
        member.organization.save()
