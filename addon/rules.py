"""
Rules: Módulo afiliados
"""

from base.models import RuleChecker, RuleIntegrityError


# ========================== OPTIONAL e PRICE =============================== #
class MustDateEndAfterDateStart(RuleChecker):
    """
    Regra: a data final deve ser posterior à data inicial.
    """

    def check(self, model_instance, *args, **kwargs):
        if model_instance.date_start >= model_instance.date_end:
            raise RuleIntegrityError('Data inicial deve ser anterior a data final.')


# =============================== PRICE ===================================== #
class MustLotCategoryBeAmongOptionalLotCategories(RuleChecker):
    """
    Regra: o LotCategory de Price deve estar entre os LotCategory da relação
    N-N do Optional Informado.
    """

    def check(self, model_instance, *args, **kwargs):
        if model_instance._state.adding is False:
            return

        if hasattr(model_instance, 'optional_product'):
            optional = model_instance.optional_product
        else:
            optional = model_instance.optional_service

        lot_category = model_instance.lot_category
        lot_pks = [lc.pk for lc in optional.lot_categories.all()]

        if lot_category.pk not in lot_pks:
            raise RuleIntegrityError(
                'Você deve informar uma categoria de lote que já esteja'
                ' inserida no opcional "{}".'.format(optional.name)
            )


class MustHaveUniqueDatetimeInterval(RuleChecker):
    """
    Regra: o Price cadastrado não pode chocar com outro vinculado ao seu
    Opcional.
    """

    def check(self, model_instance, *args, **kwargs):
        if model_instance._state.adding is False:
            return

        if hasattr(model_instance, 'optional_product'):
            optional = model_instance.optional_product
        else:
            optional = model_instance.optional_service

        conflict_prices = []
        for price in optional.prices.all():
            price_str = 'R$ {:.2f}'.format(round(price.price, 2))
            price_str += ' - {} a {}'.format(
                price.date_start.strftime('%d/%m/%Y %H:%M'),
                price.date_end.strftime('%d/%m/%Y %H:%M'),
            )

            if model_instance.date_start >= price.date_start \
                    and model_instance.date_end <= price.date_end:
                conflict_prices.append(price_str)
                continue

        if conflict_prices:
            raise RuleIntegrityError(
                'As datas informadas conflitam com outro(s) preço(s) já'
                ' existente(s) para este Opcional.'
                ' O(s) preço(s) é(são): {}.'.format('; '.join(conflict_prices))
            )


# ===================== SUBSCRIPTION OPTIONAL =============================== #
class MustBeSameOptionalLotCategory(RuleChecker):
    """
    Regra: a Inscrição com o Opcional devem pertencener ao mesmo LotCategory.
    """

    def check(self, model_instance, *args, **kwargs):
        if model_instance._state.adding is False:
            return

        if hasattr(model_instance, 'optional_product'):
            optional = model_instance.optional_product
        else:
            optional = model_instance.optional_service

        sub = model_instance.subscription
        lot_category = sub.lot.category

        lot_pks = [lc.pk for lc in optional.lot_categories.all()]

        if lot_category.pk not in lot_pks:
            raise RuleIntegrityError(
                'Você deve informar uma categoria de lote que já esteja'
                ' inserida no opcional "{}".'.format(optional.name)
            )
