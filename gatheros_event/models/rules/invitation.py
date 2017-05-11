from django.core.exceptions import ValidationError
from django.db import IntegrityError


def rule_1_organizacao_internas_nao_pode_ter_convites(entity):
    if entity.author.organization.internal is True:
        raise IntegrityError(
            'Não é permitido criar convites para uma organização interna.')


def rule_2_nao_pode_mudar_autor(entity):
    if entity.pk and entity.has_changed('author'):
        raise ValidationError({'author': [
            'Não é permitido mudar o autor de um convite.']})


def rule_3_nao_pode_mudar_convidado(entity):
    if entity.pk and entity.has_changed('to'):
        raise ValidationError({'to': [
            'Não é permitido mudar o convidado de um convite.']})


def rule_4_administrador_nao_pode_se_convidar(entity):
    author = entity.author.person

    if author == entity.to.person:
        raise ValidationError(
            {'to': [
                'Não é permitido um administrador se convidar para uma '
                'organização.'
            ]}
        )


def rule_5_nao_deve_existir_2_convites_para_usuario_organizacao(entity,
                                                                adding=True):
    if adding is True and entity.has_previous() is True:
        raise ValidationError(
            {'to': [
                'Já existe um convite para o usuário \'{}\' '
                'na organização \'{}\'.'.format(
                    entity.author.organization.name,
                    entity.to.person.name
                )
            ]}
        )


def rule_6_autor_deve_ser_membro_admin(entity, adding=True):
    organization = entity.author.organization
    person = entity.author.person

    if adding and not organization.is_admin(person):
        raise ValidationError({'author': [
            'Somente administradores podem convidar novos membros.']})


def rule_7_nao_deve_convidar_um_membro_da_organizacao(entity, adding=True):
    organization = entity.author.organization
    person = entity.to.person

    if adding and organization.is_member(person):
        raise ValidationError(
            {'to': [
                'Não é permitido convidar \'{}\' para a organização '
                '\'{}\' pois ele já é membro.'.format(
                    person.name,
                    organization.name
                )
            ]})
