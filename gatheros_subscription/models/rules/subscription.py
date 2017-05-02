from django.db import IntegrityError


def rule_1_limite_lote_excedido( subscription ):
    lot = subscription.lot
    limit = lot.limit
    if limit and int(limit) > 0 and int(lot.subscriptions.count()) >= limit:
        raise IntegrityError('O lote atingiu o limite de inscrições.')


def rule_2_codigo_inscricao_deve_ser_gerado( subscription ):
    if not subscription.code:
        raise IntegrityError('Código de inscrição não encontrado.')


def rule_3_numero_inscricao_gerado( subscription ):
    if not subscription.count:
        raise IntegrityError('Número sequencial inscrição não encontrado.')


def rule_4_inscricao_confirmada_com_data_confirmacao( subscription ):
    attended = subscription.attended
    attended_on = subscription.attended_on
    if (attended and not attended_on) or (not attended and attended_on):
        raise IntegrityError('Inscrições com confirmação de presença precisam ter data de confirmação e vice-versa.')
