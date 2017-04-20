from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError

from gatheros_event.models import Person


def split_name(name):
    names = name.split(' ')
    last_name = names[-1]
    names.pop()
    first_name = " ".join(names)
    return {'first': first_name, 'last': last_name}


@receiver(pre_save, sender=Person)
def add_related_user_when_has_user(sender, instance, raw, **_):
    """
    Verifica se a instância de Person possui informações necessárias para vincular User

    :param sender:
    :param instance:
    :param raw:
    :param _:
    :return:
    """
    # Disable when loaded by fixtures
    if raw is True:
        return

    if instance.has_user:
        if not instance.email:
            raise ValidationError({'email': ['Informe o e-mail para vincular um usuário']})

        if instance.user and instance.user.email == instance.email:
            return None

        if User.objects.filter(username=instance.email).count() > 0:
            raise ValidationError({'email': ['Informe o e-mail para vincular um usuário']})

        names = split_name(instance.name)

        try:
            instance.user = User.objects.get(username=instance.email, email=instance.email)
        except User.DoesNotExist:
            instance.user = User.objects.create(
                first_name=names.get('first'),
                last_name=names.get('last'),
                email=instance.email,
                username=instance.email,
                is_active=False
            )


@receiver(post_save, sender=Person)
def update_user_related_name(sender, instance, created, raw, **_):
    """
    Atualiza o nome de Usuário assim que o nome da pessoa é atualizado.

    :param sender:
    :param instance:
    :param created:
    :param raw:
    :param _:
    :return:
    """
    # Disable when loaded by fixtures
    if raw is True:
        return

    names = split_name(instance.name)

    if not instance.user:
        return None

    instance.user.first_name = names.get('first')
    instance.user.last_name = names.get('last')
    instance.user.save()
