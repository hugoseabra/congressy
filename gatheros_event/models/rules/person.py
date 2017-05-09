from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


def rule_1_has_user_deve_ter_email(entity):
    if entity.has_user and not entity.email:
        raise ValidationError({'email': [
            'Informe um e-mail para vincular a pessoa a um usuário'
        ]})


def rule_2_ja_existe_outro_usuario_com_mesmo_email(entity):
    if entity.has_user is True \
            and entity.has_changed('email') \
            and User.objects.filter(email=entity.email).exists():
        raise ValidationError({'email': [
            'Já existe um usuário ativo com o e-mail {}.'.format(entity.email)
        ]})


def rule_3_nao_remove_usuario_uma_vez_relacionado(entity):
    """
    Devido a um excesso de validações que são necessárias para desvincular um
    usuário e depois, caso queira se vincular novamente (tendo de reaproveitar
    o registro), fez-se necessário não permitir mais que um usuário, uma vez
    relacionado não seja mais desvinculado.
    """
    if entity.has_changed('has_user') and entity.old_value('has_user') is True:
        raise ValidationError({'has_user': [
            'Não é possível desvincular o usuário.'
        ]})


def rule_4_desativa_usuario_ao_deletar_pessoa(entity):
    """
    Usuário permamancerá no sistema pois pode haver vários registro ligados a
    ele que são importantes serem mantidos. Se a mesma pessoa (com o mesmo
    e-mail) quiser retornar ao sistema, o mesmo usuário poderá ser relacionado.
    """
    if entity.user and entity.user.is_active is True:
        entity.user.is_active = False
        entity.user.save()
