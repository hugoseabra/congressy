from django.forms import ValidationError

from base import managers
from core.util.date import DateTimeRange
from .models import (
    OptionalProduct,
    OptionalService,
    OptionalType,
    ProductPrice,
    ServicePrice,
    Session,
    SubscriptionOptionalService,
    SubscriptionOptionalProduct,
    Theme,
)


class ThemeManager(managers.Manager):
    """ Manager de themas. """

    class Meta:
        model = Theme
        fields = '__all__'


class OptionalTypeManager(managers.Manager):
    """ Manager de tipos de opcionais """

    class Meta:
        model = OptionalType
        fields = '__all__'


class OptionalProductManager(managers.Manager):
    """ Manager de produtos opcionais. """

    class Meta:
        model = OptionalProduct
        fields = '__all__'


class OptionalServiceManager(managers.Manager):
    """ Manager de serviços opcionais """

    class Meta:
        model = OptionalService
        fields = '__all__'


class SubscriptionOptionalServiceManager(managers.Manager):
    """ Manager de serviços opcionais de inscrições"""

    class Meta:
        model = SubscriptionOptionalService
        fields = '__all__'

    def clean(self):
        """
        Implementação da regras:

            Regra #1: Se quantidade de inscrições já foi atingida,
                novas inscrições não poderão ser realizadas
            Regra #2: Validar restrição de sessão se há restrição por Sessão,
                ou seja, se há outro Optional dentro do mesmo intervalo de
                data e hora final e inicial do Optional informado.
            Regra #3: Validar restrição por tema (LimitByTheme), se há
             restrição por Tema, ou seja, se o Participante já possui X
             opcionais no mesmo tema e não pode mais se cadastrar em outro.

        """
        cleaned_data = super().clean()

        optional_service = cleaned_data['optional_service']
        subscription = cleaned_data['subscription']
        total_subscriptions = optional_service.subscription_services.count()
        quantity = optional_service.quantity or 0

        # Regra 1:
        if 0 < quantity <= total_subscriptions:
            raise ValidationError(
                'Quantidade de inscrições já foi atingida, novas inscrições '
                'não poderão ser realizadas'
            )

        # Regra 2:
        if optional_service.session.restrict_unique:

            new_start = optional_service.session.date_start
            new_end = optional_service.session.date_end

            for optional in subscription.subscriptionoptionalservice.all():

                start = optional.optional_service.session.date_start
                stop = optional.optional_service.session.date_end

                session_range = DateTimeRange(start=start, stop=stop)

                if new_start in session_range or new_end in session_range:
                    raise ValidationError(
                        'Conflito de horário: o inicio do opcional {} '
                        'está dentro da sessão do opcional {}.'.format(
                            optional_service.name,
                            optional.optional_service.name))

        # Regra 3:
        if optional_service.theme.limit:

            total = 0

            for optional in subscription.subscriptionoptionalservice.all():

                if optional.optional_service.theme == optional_service.theme:
                    total += 1

            if total >= optional_service.theme.limit:
                raise ValidationError(
                    'Limite por tema excedido: limite do ''tema {} já foi '
                    'atingido'.format(optional_service.theme.name)
                )

        return cleaned_data


class SubscriptionOptionalProductManager(managers.Manager):
    """ Manager de produtos opcionais de inscrições """

    class Meta:
        model = SubscriptionOptionalProduct
        fields = '__all__'

    def clean(self):
        """
        Implementação da regra:

            Se quantidade de inscrições já foi atingida, novas inscrições
            não poderão ser realizadas

        """
        cleaned_data = super().clean()

        optional_product = cleaned_data['optional_product']
        num_subs = optional_product.subscription_products.count()
        quantity = optional_product.quantity or 0
        if 0 < quantity <= num_subs:
            raise ValidationError(
                'Quantidade de inscrições já foi atingida, '
                'novas inscrições não poderão ser realizadas')

        return cleaned_data
