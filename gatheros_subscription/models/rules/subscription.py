# pylint: disable=C0103
"""Regras de Negócios para inscrição."""

from datetime import datetime

from django.db import IntegrityError


def rule_1_limite_lote_excedido(subscription):
    """
    Se limite do lote foi excedido, não se deve aceitar novas inscrições.
    """
    lot = subscription.lot
    limit = lot.limit
    num = lot.subscriptions.filter(completed=True).exclude(
        status=subscription.CANCELED_STATUS
    ).count()
    if limit and int(limit) > 0 and int(num) >= limit:
        raise IntegrityError('O lote atingiu o limite de inscrições.')


def rule_2_codigo_inscricao_deve_ser_gerado(subscription):
    """
    Código de inscrição deve sempre ser gerado.
    """
    if not subscription.code:
        raise IntegrityError('Código de inscrição não encontrado.')


def rule_3_numero_inscricao_gerado(subscription):
    """
    Número de inscrição deve ser gerado.
    """
    if not subscription.count:
        raise IntegrityError('Número sequencial inscrição não encontrado.')


def rule_4_inscricao_confirmada_com_data_confirmacao(subscription):
    """
    Inscrição confirmada deve possuir data de confirmação de inscrição.
    """
    attended = subscription.attended
    attended_on = subscription.attended_on
    if (attended and not attended_on) or (not attended and attended_on):
        raise IntegrityError(
            'Inscrições com confirmação de presença precisam ter data de'
            ' confirmação e vice-versa.'
        )


def rule_5_inscricao_apos_data_final_lote(subscription, adding=False):
    """
    Inscrição após data final do lote não deve ser aceita.
    """
    if adding and subscription.lot.date_end < datetime.now():
        raise IntegrityError(
            'O lote já foi encerrado e não pode mais ter inscrições.'
        )


def rule_6_inscricao_apos_data_final_evento(subscription, adding=False):
    """
    Inscrição após data final de evento não deve ser aceito.
    """
    if adding and subscription.lot.event.date_end < datetime.now():
        raise IntegrityError(
            'O evento já foi encerrado e não pode mais ter inscrições.'
        )
