from django.db import IntegrityError
from django.core.exceptions import ValidationError
from gatheros_event.models import Event


def rule_1_event_inscricao_desativada( lot ):
    if lot.event.subscription_type == Event.SUBSCRIPTION_DISABLED:
        raise ValidationError({'event': ['O evento selecionado possui inscrições desativadas']})


def rule_2_mais_de_1_lote_evento_inscricao_simples( lot ):
    """
    Não permite mais de um lote em eventos de inscrições simples.
    """
    if lot.pk:
        # Se edição, verificar se o evento possui o lote em questão
        error = not lot.event.lots.filter(pk=lot.pk).exists()
    else:
        # Caso não possua, verificar se o evento de inscrição simples já possui lote
        error = lot.event.subscription_type == Event.SUBSCRIPTION_SIMPLE and lot.event.lots.count() > 0

    if error:
        raise IntegrityError('Não é possível inserir mais de um lote em evento com inscrições simples.')


def rule_3_evento_inscricao_simples_nao_pode_ter_lot_externo( lot ):
    if lot.event.subscription_type == lot.event.SUBSCRIPTION_SIMPLE and lot.internal is False:
        raise ValidationError(
            {'internal': ['Lote não pode ser interno para evento com inscrições simples.']})


def rule_4_evento_inscricao_por_lotes_nao_ter_lot_interno( lot ):
    if lot.event.subscription_type == lot.event.SUBSCRIPTION_BY_LOTS and lot.internal is True:
        raise ValidationError(
            {'internal': ['O evento possui inscrições por lotes, portanto o lote não pode ser interno.']}
        )


def rule_5_data_inicial_antes_data_final( lot ):
    if lot.date_start > lot.date_end:
        raise ValidationError({'date_start': ['A data inicial deve ser anterior a data final do lote.']})


def rule_6_data_inicial_antes_data_inicial_evento( lot ):
    if lot.date_start > lot.event.date_start:
        raise ValidationError({'date_start': ['A data inicial do lote deve ser anterior a data inicial do evento']})


def rule_7_data_final_antes_data_inicial_evento( lot ):
    if lot.date_end and lot.date_end > lot.event.date_start:
        raise ValidationError({'date_end': ['A data final do lote deve ser anterior a data inicial do evento']})


def rule_8_lot_interno_nao_pode_ter_preco( lot ):
    if lot.internal and lot.price:
        raise ValidationError({'price': ['Lotes internos devem ser gratuitos. Deixe o preço vazio.']})


def rule_9_lote_pago_deve_ter_limite( lot ):
    if lot.price and not lot.limit:
        raise ValidationError({'limit': ['Lotes com inscrições pagas devem possuir um limite de público.']})


def rule_10_lote_privado_deve_ter_codigo_promocional( lot ):
    if lot.private and not lot.promo_code:
        raise ValidationError({'promo_code': ['Lotes privados devem possui um código promocional para acessá-lo.']})
