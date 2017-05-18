from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from gatheros_event.models import Person


def split_name(name):
    names = name.split(' ')
    last_name = names[-1]
    names.pop()
    first_name = " ".join(names)
    return {'first': first_name, 'last': last_name}


@receiver(pre_save, sender=Person)
def add_related_user_when_has_user(instance, raw, **_):
    """
    Verifica se a instância de Person possui informações necessárias para
    vincular User

    :param instance:
    :param raw:
    :param _:
    :return:
    """
    # Disable when loaded by fixtures
    if raw is True:
        return

    if instance.has_user:
        if instance.user and instance.user.email == instance.email:
            return

        if User.objects.filter(username=instance.email).count() > 0:
            raise ValidationError({'email': [
                'Já existe um usuário ativo com o e-mail'
                ' {}.'.format(instance.email)
            ]})

        names = split_name(instance.name)

        try:
            user = User.objects.get(email=instance.email)

            """
            Um usuário poderá ter sido de outra pessoa. Se a pessoa
            possui acesso ao mesmo e-mail, então iremos deixar o registro ser
            processado. Porém, teremos de garantir que a pessoa possui acesso
            ao e-mail informado.
            """
            user.is_active = False

            user.first_name = names.get('first')
            user.last_name = names.get('last')
            user.save()

            instance.user = user

        except User.DoesNotExist:
            instance.user = User.objects.create(
                first_name=names.get('first'),
                last_name=names.get('last'),
                email=instance.email,
                username=instance.email,
                is_active=False
            )

    else:
        if instance.user:
            # disable user
            instance.user.is_active = False
            instance.user.save()

        instance.user = None


@receiver(post_save, sender=Person)
def update_user_related_name(instance, raw, **_):
    """
    Atualiza o nome de Usuário assim que o nome da pessoa é atualizado.
    """
    # Disable when loaded by fixtures
    if raw is True \
            or not instance.user \
            or instance.has_changed('name') is False:
        return

    names = split_name(instance.name)

    instance.user.first_name = names.get('first')
    instance.user.last_name = names.get('last')
    instance.user.save()
