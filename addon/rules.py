"""
Rules: Módulo afiliados
"""

from base.models import RuleChecker, RuleIntegrityError


# ========================== SESSION e PRICE ================================ #
class MustDateEndAfterDateStart(RuleChecker):
    """
    Regra: a data final deve ser posterior à data inicial.
    """

    def check(self, model_instance, *args, **kwargs):
        if model_instance.date_start >= model_instance.date_end:
            raise RuleIntegrityError(
                'Data inicial deve ser anterior a data final.'
            )


# ============================= OPTIONAL ==================================== #
def check_dates_conflict(optional, other_optionals):
    conflict_prices = []
    for o_optional in other_optionals.all():
        optional_str = '{} - {} a {}'.format(
            o_optional.name,
            o_optional.date_start.strftime('%d/%m/%Y %H:%M'),
            o_optional.date_end.strftime('%d/%m/%Y %H:%M'),
        )

        date_start = o_optional.date_start
        date_end = o_optional.date_end

        dt_start_conflicts = \
            date_start <= optional.date_start <= o_optional.date_end

        dt_end_conflicts = \
            date_end <= optional.date_end <= o_optional.date_end

        if dt_start_conflicts or dt_end_conflicts:
            conflict_prices.append(optional_str)

    if conflict_prices:
        raise RuleIntegrityError(
            'As datas informadas conflitam com outro(s) opcionais(s) já'
            ' existente(s): {}'.format('; '.join(conflict_prices))
        )


class ProductMustHaveUniqueDatetimeInterval(RuleChecker):
    """
    Regra: o opcional de produto cadastrado não pode chocar com outro na mesma
    categoria de lote.
    """

    def check(self, model_instance, *args, **kwargs):
        if model_instance._state.adding is False:
            date_start_changed = model_instance.has_changed('date_start')
            date_end_changed = model_instance.has_changed('date_end')

            if not date_start_changed and not date_end_changed:
                return

        lot_category = model_instance.lot_category
        check_dates_conflict(model_instance, lot_category.product_optionals)


class ServiceMustHaveUniqueDatetimeInterval(RuleChecker):
    """
    Regra: o opcional de serviço cadastrado não pode chocar com outro na mesma
    categoria de lote.
    """

    def check(self, model_instance, *args, **kwargs):
        if model_instance._state.adding is False:
            date_start_changed = model_instance.has_changed('date_start')
            date_end_changed = model_instance.has_changed('date_end')

            if not date_start_changed and not date_end_changed:
                return

        lot_category = model_instance.lot_category
        check_dates_conflict(model_instance, lot_category.service_optionals)


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
