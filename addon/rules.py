"""
Rules: Módulo afiliados
"""
from datetime import datetime
from addon import constants
from base.models import RuleChecker, RuleIntegrityError


# ========================== SESSION e PRICE ================================ #
class MustScheduleDateEndAfterDateStart(RuleChecker):
    """
    Regra: a data final da programação deve ser posterior à data inicial.
    """

    def check(self, model_instance, *args, **kwargs):
        if model_instance.schedule_start >= model_instance.schedule_end:
            raise RuleIntegrityError(
                'Data/hora inicial deve ser anterior a data/hora final.'
            )


# ============================= OPTIONAL ==================================== #
class ServiceMustHaveUniqueDatetimeScheduleInterval(RuleChecker):
    """
    Regra: o opcional de serviço cadastrado não pode chocar com outro na mesma
    categoria de lote.
    """

    def check(self, model_instance, *args, **kwargs):
        if model_instance._state.adding is False:
            schedule_start_changed = \
                model_instance.has_changed('schedule_start')
            schedule_end_changed = \
                model_instance.has_changed('schedule_end')

            if not schedule_start_changed and not schedule_end_changed:
                return

        lot_category = model_instance.lot_category

        optional = model_instance
        other_optionals = lot_category.service_optionals.all()

        conflict_prices = []
        for o_optional in other_optionals:
            optional_str = '{} - {} a {}'.format(
                o_optional.name,
                o_optional.schedule_start.strftime('%d/%m/%Y %H:%M'),
                o_optional.schedule_end.strftime('%d/%m/%Y %H:%M'),
            )

            date_start = o_optional.schedule_start
            date_end = o_optional.schedule_end

            dt_start_conflicts = \
                date_start <= optional.schedule_start <= o_optional.schedule_end

            dt_end_conflicts = \
                date_end <= optional.schedule_end <= o_optional.schedule_end

            if dt_start_conflicts or dt_end_conflicts:
                conflict_prices.append(optional_str)

        if conflict_prices:
            raise RuleIntegrityError(
                'Conflito de horários de programação: as datas informadas'
                ' conflitam com outro(s) opcionais(s) de serviço já'
                ' existente(s) para esta mesma categoria de lote: {}'.format(
                    '; '.join(conflict_prices)
                )
            )


class OptionalMustHaveMinimumDays(RuleChecker):
    """
    Regra: o opcional deve ter o valor do 'release_days' com valor do mínimo
    configurado.
    """

    def check(self, model_instance, *args, **kwargs):
        if model_instance.release_days < constants.MINIMUM_RELEASE_DAYS:
            raise RuleIntegrityError(
                'O número de dias de liberação de opcionais para inscrições'
                ' não confirmadas deve ser, no mínimo, "{}" dias.'.format(
                    constants.MINIMUM_RELEASE_DAYS
                )
            )


# ===================== SUBSCRIPTION OPTIONAL =============================== #
class MustBeSameOptionalLotCategory(RuleChecker):
    """
    Regra: a Inscrição com o Opcional devem pertencener ao mesmo LotCategory.
    """

    def check(self, model_instance, *args, **kwargs):
        optional = model_instance.optional

        sub = model_instance.subscription

        if optional.lot_category.pk != sub.lot.category.pk:
            raise RuleIntegrityError(
                'Você deve informar uma categoria de lote que já esteja'
                ' inserida no opcional "{}".'.format(optional.name)
            )

