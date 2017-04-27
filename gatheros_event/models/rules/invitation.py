from django.core.exceptions import ValidationError
from django.db import IntegrityError


def rule_1_organizacao_internas_nao_pode_ter_convites(entity):
    if entity.author.organization.internal is True:
        raise IntegrityError('Organizações internas não aceitam convites')


def rule_2_nao_pode_mudar_autor(entity):
    if entity.pk and entity.has_changed('author'):
        raise ValidationError({'author': ['Você não pode mudar o autor de um convite existente.']})


def rule_3_nao_pode_mudar_convidado(entity):
    if entity.pk and entity.has_changed('to'):
        raise ValidationError({'to': ['Você não pode mudar o convidado de um convite existente.']})


def rule_4_autor_convida_a_si_mesmo(entity):
    author_person = entity.author.person
    invited_person = entity.to.person

    if author_person == invited_person:
        raise ValidationError(
            {'to': ['O autor \'{}\' não pode convidar a si mesmo para uma organização'.format(author_person.name)]}
        )


def rule_5_convite_ja_existente(entity, adding=True):
    if adding is True and entity.has_previous() is True:
        raise ValidationError(
            {'to': [
                'Já existe um convite da organização \'{}\' para \'{}\' como \'{}\''.format(
                    entity.author.organization.name,
                    entity.to.person.name,
                    entity.get_type_display()
                )
            ]}
        )


def rule_6_autor_deve_ser_membro_admin(entity, adding=True):
    organization = entity.author.organization
    person = entity.author.person
    group = entity.author.ADMIN

    if adding and _is_organization_member(organization=organization, person=person, group=group) is False:
        raise ValidationError({'author': ['O autor do convite deve ser um membro administrador da organização']})


def rule_7_convidado_ja_membro_da_organizacao(entity, adding=True):
    organization = entity.author.organization
    person = entity.to.person

    if adding and _is_organization_member(organization=organization, person=person) is True:
        raise ValidationError({'to': ['\'{}\' já é membro da organização \'{}\''.format(person.name, organization.name)]})


def _is_organization_member(organization, person, group=None):
    return organization.get_member_by_person(person=person, group=group) is not None
