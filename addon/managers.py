from django.forms import ValidationError

from base import managers
from .models import (
    OptionalProduct,
    OptionalService,
    OptionalType,
    ProductPrice,
    ServicePrice,
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


class ProductPriceManager(managers.Manager):
    """ Manager de preços. """

    class Meta:
        model = ProductPrice
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        """
            Optional: se tiver "prices", o campo has_cost deve ser True
        """

        optional_product = cleaned_data['optional_product']
        optional_product.has_cost = True
        optional_product.save()

        return cleaned_data


class ServicePriceManager(managers.Manager):
    """ Manager de preços. """

    class Meta:
        model = ServicePrice
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        """
            Optional: se tiver "prices", o campo has_cost deve ser True
        """

        optional_service = cleaned_data['optional_service']
        optional_service.has_cost = True
        optional_service.save()

        return cleaned_data


class SubscriptionOptionalServiceManager(managers.Manager):
    """ Manager de serviços opcionais de inscrições"""

    class Meta:
        model = SubscriptionOptionalService
        fields = '__all__'

    def clean(self):
        """
        Implementação da regra:

            Se quantidade de inscrições já foi atingida, novas inscrições
            não poderão ser realizadas

        """
        cleaned_data = super().clean()

        optional_service = cleaned_data['optional_service']

        num_subs = optional_service.subscription_services.count()

        if num_subs >= optional_service.quantity:
            raise ValidationError(
                'Quantidade de inscrições já foi atingida, novas inscrições '
                'não poderão ser realizadas')

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
        if num_subs >= optional_product.quantity:
            raise ValidationError(
                'Quantidade de inscrições já foi atingida, '
                'novas inscrições não poderão ser realizadas')

        return cleaned_data
