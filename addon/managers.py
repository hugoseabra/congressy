from datetime import datetime

from django.forms import ValidationError

from base import managers
from core.util.date import DateTimeRange
from .constants import MINIMUM_RELEASE_DAYS
from .models import (
    Product,
    Service,
    OptionalProductType,
    OptionalServiceType,
    SubscriptionService,
    SubscriptionProduct,
    Theme,
)


class ThemeManager(managers.Manager):
    """ Manager de themas. """

    class Meta:
        model = Theme
        fields = '__all__'


class OptionalProductTypeManager(managers.Manager):
    """ Manager de tipos de opcionais """

    class Meta:
        model = OptionalProductType
        fields = '__all__'


class OptionalServiceTypeManager(managers.Manager):
    """ Manager de tipos de opcionais """

    class Meta:
        model = OptionalServiceType
        fields = '__all__'


class ProductManager(managers.Manager):
    """ Manager de produtos opcionais. """

    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, **kwargs):
        initial = kwargs.get('initial', {})
        if not kwargs.get('instance') and initial.get('release_days') is None:
            initial.update({'release_days': MINIMUM_RELEASE_DAYS})
            kwargs.update({'initial': initial})

        super().__init__(**kwargs)


class ServiceManager(managers.Manager):
    """ Manager de serviços opcionais """

    class Meta:
        model = Service
        fields = '__all__'


class SubscriptionServiceManager(managers.Manager):
    """ Manager de serviços opcionais de inscrições"""

    class Meta:
        model = SubscriptionService
        fields = '__all__'

    def clean(self):
        """

        Regra #1: Se quantidade de inscrições já foi atingida,
            novas inscrições não poderão ser realizadas

        Regra #2: Validar restrição de sessão se há restrição por Sessão,
            ou seja, se há outro Optional dentro do mesmo intervalo de
            data e hora final e inicial do Optional informado.

        Regra #3: Validar rest-rição por tema (LimitByTheme), se há
            restrição por Tema, ou seja, se o Participante já possui X
            opcionais no mesmo tema e não pode mais se cadastrar em outro.

        Regra #4:
            Deve restringir a criação de inscrições em opcionais caso o
            opcional selecionado esteja com a data/hora final antes da
            data/hora atual.

        """
        cleaned_data = super().clean()

        optional_service = cleaned_data['optional']
        subscription = cleaned_data['subscription']
        total_subscriptions = optional_service.services.count()
        quantity = optional_service.quantity or 0

        # Regra 1:
        if 0 < quantity <= total_subscriptions:
            raise ValidationError(
                'Quantidade de inscrições já foi atingida, novas inscrições '
                'não poderão ser realizadas'
            )

        # Regra 2:
        new_start = optional_service.schedule_start
        new_end = optional_service.schedule_end

        is_restricted = optional_service.restrict_unique

        for sub_optional in subscription.subscriptionservice.all():

            start = sub_optional.optional.schedule_start
            stop = sub_optional.optional.schedule_end
            is_sub_restricted = \
                sub_optional.optional.restrict_unique

            session_range = DateTimeRange(start=start, stop=stop)
            has_conflict = (new_start in session_range or new_end in
                            session_range)

            if has_conflict is True and (is_restricted or is_sub_restricted):
                raise ValidationError(
                    'Conflito de horário: o opcional "{}" '
                    'está em conflito com o opcional "{}".'.format(
                        optional_service.name,
                        sub_optional.optional.name
                    )
                )

        # Regra 3:
        if optional_service.theme.limit:

            total = 0

            for optional in subscription.subscriptionservice.all():

                if optional.optional.theme == optional_service.theme:
                    total += 1

            if total >= optional_service.theme.limit:
                raise ValidationError(
                    'Limite por tema excedido: limite do ''tema {} já foi '
                    'atingido'.format(optional_service.theme.name)
                )

        # Regra 4
        if optional_service.date_end_sub and \
                datetime.now() > optional_service.date_end_sub:
            raise ValidationError(
                'Este opcional já expirou e não aceita mais inscrições.'
            )

        return cleaned_data


class SubscriptionProductManager(managers.Manager):
    """ Manager de produtos opcionais de inscrições """

    class Meta:
        model = SubscriptionProduct
        fields = '__all__'

    def clean(self):
        """
        Regra #1:
            Se quantidade de inscrições já foi atingida, novas inscrições
            não poderão ser realizadas

        Regra #2:
            Deve restringir a criação de inscrições em opcionais caso o
            opcional selecionado esteja com a data/hora final antes da
            data/hora atual.

        """
        cleaned_data = super().clean()

        product = cleaned_data['optional']

        # Regra 1
        num_subs = product.products.count()
        quantity = product.quantity or 0
        if 0 < quantity <= num_subs:
            raise ValidationError(
                'Quantidade de inscrições já foi atingida, '
                'novas inscrições não poderão ser realizadas')

        # Regra 2
        if product.date_end_sub and datetime.now() > product.date_end_sub:
            raise ValidationError(
                'Este opcional já expirou e não aceita mais inscrições.'
            )

        return cleaned_data
