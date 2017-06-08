"""
Regras de negócio dos modelos.
"""

from . import event, invitation, member


def check_invite(entity):
    """
    Regras para validação de convites

    :param entity:
    """
    invitation.rule_1_organizacao_internas_nao_pode_ter_convites(entity)
    invitation.rule_2_nao_pode_mudar_autor(entity)
    invitation.rule_3_nao_pode_mudar_convidado(entity)
    invitation.rule_4_administrador_nao_pode_se_convidar(entity)
    invitation.rule_5_nao_deve_existir_2_convites_para_mesmo_usuario(entity)
    invitation.rule_6_autor_deve_ser_membro_admin(entity)
    invitation.rule_7_nao_deve_convidar_um_membro_da_organizacao(entity)
