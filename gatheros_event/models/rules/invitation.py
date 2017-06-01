# pylint: disable=C0103
"""
Regras de negócio para convite.
"""

from django.core.exceptions import ValidationError
from django.db import IntegrityError


def rule_1_organizacao_internas_nao_pode_ter_convites(entity):
    """
    Organização interna não pode convidar outros membros
    :param entity:
    """
    if entity.author.organization.internal is True:
        raise IntegrityError(
            'Não é permitido criar convites para uma organização interna.')


def rule_2_nao_pode_mudar_autor(entity):
    """
    Não pode mudar o autor de um convite
    :param entity:
    """
    if entity.pk and entity.has_changed('author'):
        raise ValidationError({'author': [
            'Não é permitido mudar o autor de um convite.']})


def rule_3_nao_pode_mudar_convidado(entity):
    """
    Não pode mudar o convidado de um convite
    :param entity:
    """
    if entity.pk and entity.has_changed('to'):
        raise ValidationError({'to': [
            'Não é permitido mudar o convidado de um convite.']})


def rule_4_administrador_nao_pode_se_convidar(entity):
    """
    O administrador não pode enviar um convite para si mesmo
    :param entity:
    """
    author = entity.author.person.user

    if author == entity.to:
        raise ValidationError(
            {'to': [
                'Não é permitido um administrador se convidar para uma '
                'organização.'
            ]}
        )


def rule_5_nao_deve_existir_2_convites_para_mesmo_usuario(entity):
    """
    Não pode existir mais de um convite para o mesmo usuário em uma
    organização
    :param entity:
    """
    if entity._state.adding is True and entity.has_previous() is True:
        raise ValidationError(
            {'to': [
                'Já existe um convite para \'{}\' '
                'na organização \'{}\'.'.format(
                    entity.to.email,
                    entity.author.organization.name,
                )
            ]}
        )


def rule_6_autor_deve_ser_membro_admin(entity):
    """
    O autor de um convite deve ser um membro admin da organização
    :param entity:
    """
    organization = entity.author.organization
    person = entity.author.person

    if entity._state.adding and not organization.is_admin(person):
        raise ValidationError({'author': [
            'Somente administradores podem convidar novos membros.']})


def rule_7_nao_deve_convidar_um_membro_da_organizacao(entity):
    """
    Não deve criar um convite para um usuário que já é membro da organização
    :param entity:
    """
    organization = entity.author.organization
    user = entity.to

    if entity._state.adding and organization.is_member(user):
        raise ValidationError(
            {'to': [
                'Um membro com o email "{}" já existe na '
                'organização "{}".'.format(user.email, organization.name)
            ]})
