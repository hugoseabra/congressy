# pylint: disable=C0103
"""Regras de Negócios para lote."""

from django.core.exceptions import ValidationError
from django.db import IntegrityError

from gatheros_event.models import Event


def rule_1_category_same_event(lot):
    if lot.category and lot.category.event.pk != lot.event.pk:
        raise ValidationError({'category': [
            'A categoria do lote e o lote não estão no mesmo evento.'
        ]})


def rule_2_mais_de_1_lote_evento_inscricao_simples(lot):
    """
    Não permite mais de um lote em eventos de inscrições simples.
    """
    if lot.pk:
        return

    # Caso não possua, se evento de inscrição simples já possui lote
    error = lot.event.subscription_type == Event.SUBSCRIPTION_SIMPLE \
            and lot.event.lots.count() > 0

    if error:
        raise IntegrityError(
            'Não é possível inserir mais de um lote em evento com inscrições'
            ' simples.'
        )


def rule_3_evento_inscricao_simples_nao_pode_ter_lot_externo(lot):
    """
    Evento com inscrição simples não pode ter lote externo.
    """

    if lot.event.subscription_type == lot.event.SUBSCRIPTION_SIMPLE \
            and lot.internal is False:
        raise ValidationError({'internal': [
            'Lote não pode ser interno para evento com inscrições simples.'
        ]})


def rule_4_evento_inscricao_por_lotes_nao_ter_lot_interno(lot):
    """
    Evento com inscrição por lotes não pode ter lote interno
    """

    if lot.event.subscription_type == lot.event.SUBSCRIPTION_BY_LOTS \
            and lot.internal is True:
        raise ValidationError({'internal': [
            'O evento possui inscrições por lotes, portanto o lote não pode'
            ' ser interno.'
        ]})


def rule_5_data_inicial_antes_data_final(lot):
    """
    Data inicial do lote deve ser anterior a data final
    """
    if lot.date_start > lot.date_end:
        raise ValidationError({'date_start': [
            'A data inicial deve ser anterior a data final do lote.']})


def rule_6_data_inicial_antes_data_inicial_evento(lot):
    if lot.date_start > lot.event.date_start:
        raise ValidationError({'date_start': [
            'A data inicial do lote deve ser anterior a data inicial do evento'
        ]})


def rule_7_data_final_antes_data_inicial_evento(lot):
    """
    Data final do lote deve ser anterior a data inicial do evento.
    """
    if lot.date_end and lot.date_end > lot.event.date_start:
        raise ValidationError({'date_end': [
            'A data final do lote deve ser anterior a data inicial do evento'
        ]})


def rule_8_lot_interno_nao_pode_ter_preco(lot):
    if lot.internal and lot.price:
        raise ValidationError({'price': [
            'Lotes internos devem ser gratuitos. Deixe o preço vazio.'
        ]})


def rule_9_lote_pago_deve_ter_limite(lot):
    """
    Lote pago deve ter um limite.
    """
    if lot.price and not lot.limit:
        raise ValidationError({'limit': [
            'Lotes com inscrições pagas devem possuir um limite de público.'
        ]})


def rule_10_lote_privado_deve_ter_codigo_de_exibicao(lot):
    if lot.private and not lot.promo_code:
        raise ValidationError({'exhibition_code': [
            'Lotes privados devem possui um código promocional para acessá-lo.'
        ]})
