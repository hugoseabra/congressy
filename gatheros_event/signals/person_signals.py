from django.db.models.signals import post_save
from django.dispatch import receiver

from gatheros_event.models import Person


@receiver(post_save, sender=Person)
def update_user_related_name(instance, raw, **_):
    """
    Atualiza o nome/sobrenome do usuário quando a pessoa é atualizada.
    """
    if raw is True or not instance.user:
        return

    first = instance.name.split(' ')[0]
    last = instance.name.split(' ')[-1]

    instance.user.first_name = first
    instance.user.last_name = last if not last == first else None
    instance.user.save()
