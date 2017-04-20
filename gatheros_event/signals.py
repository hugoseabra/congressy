from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Person


def split_name(name):
    names = name.split(' ')
    last_name = names[-1]
    names.pop()
    first_name = " ".join(names)
    return {'first': first_name, 'last': last_name}


@receiver(pre_save, sender=Person)
def check_user_related_fields(sender, instance, raw, **_):
    """
    Verifica se a instância de Person possui informações necessárias para vincular User

    :param sender:
    :param instance:
    :param created:
    :param raw:
    :param _:
    :return:
    """
    if instance.has_user:
        if not instance.email:
            raise AttributeError('Informe o e-mail para vincular um usuário')

        if instance.user and instance.user.email == instance.email:
            return None

        if User.objects.filter(username=instance.email).count() > 0:
            raise AttributeError('Já existe um outro usuário com este e-mail. Tente outro.')

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

    else:
        instance.has_user = False
        instance.user = None
        # @TODO verificar forma de excluir o usuário que não possuem vínculo com Person


@receiver(post_save, sender=Person)
def update_person_related_user(sender, instance, created, raw, **_):
    """
    Atualiza o nome de Usuário assim que o nome da pessoa é atualizado.

    :param sender:
    :param instance:
    :param created:
    :param raw:
    :param _:
    :return:
    """

    names = split_name(instance.name)

    if not instance.user:
        return None

    instance.user.first_name = names.get('first')
    instance.user.last_name = names.get('last')
    instance.user.save()


@receiver(post_save, sender=Person)
def update_person_related_organization(sender, instance, created, raw, **_):
    """
    Atualiza nomes de Organização e Usuário assim que o nome da
    pessoa é atualizado.
    """

    for member in instance.members.all():
        if not member.organization.internal:
            continue

        member.organization.name = instance.name
        member.organization.save()
