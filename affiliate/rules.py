"""
Rules: Módulo afiliados
"""
from decimal import Decimal
from django.db.utils import IntegrityError

from base.models import RuleChecker, RuleIntegrityError


# ============================= AFILIAÇÃO =================================== #
class MustProvideMaxPercentAffiliationRule(RuleChecker):
    """
    Regra: o valor máximo de participação de afiliação deve ser informado.
    """

    def check(self, model_instance, *args, **kwargs):
        if not model_instance.AFFILIATE_MAX_PERCENTAGE:
            raise RuleIntegrityError(
                'Percentual máximo de participação do afiliado no evento deve'
                ' ser informado'
            )


class MaxParticipationExceededAffiliationRule(RuleChecker):
    """
    Regra: afiliação não pode exceder o máximo de participação de um afiliado
    em um evento.
    """

    def check(self, model_instance, *args, **kwargs):
        participation = \
            round(Decimal(model_instance.AFFILIATE_MAX_PERCENTAGE), 2)

        if model_instance.percent > participation:
            raise RuleIntegrityError(
                'A participação percentual de afiliação não pode ultrapassar'
                ' o limite de {0:.2f}%'.format(participation)
            )
