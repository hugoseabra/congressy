from django.db import IntegrityError


def rule_1_membros_deve_ter_usuarios(entity):
    if entity.person.user is None:
        raise IntegrityError('Pessoa sem usuário não pode participar de organizações')


def rule_2_organizacao_interna_apenas_1_membro(entity, adding=True):
    """
    Organizações internas, por ser de uma pessoa apenas, não podem possuir mais de 1 membro.
    """
    if adding is True \
            and entity.organization.internal is True \
            and entity.organization.members.count() > 0:
        raise IntegrityError('Esta organização interna não pode ter membros.')


def rule_3_organizacao_interna_unico_membro_admin(entity, adding=True):
    """
    Organizações internas, por ser de uma pessoa apenas, seu único membro deve ser ADMIN
    """
    if adding is True and entity.organization.internal is True and entity.group != entity.ADMIN:
        raise IntegrityError('Membro de organização interna deve ser \'{}\''.format(entity.ADMIN))


def rule_4_nao_remover_member_organizacao_interna(entity):
    """
    Organizações internas, por ser de uma pessoa apenas, não pode fiar sem membros. 
    """
    if entity.organization.internal is True:
        raise IntegrityError(
            'Impossível remover membro. Organização interna deve possuir um membro ADMIN principal.'
        )
